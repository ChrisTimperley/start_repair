__all__ = ['transformations', 'search']

from datetime import timedelta
import logging
import random

from bugzoo.core.fileline import FileLine
from bugzoo.core.coverage import TestSuiteCoverage
from bugzoo.manager import BugZoo
from start_core.scenario import Scenario
from darjeeling.localization import Localization
from darjeeling.problem import Problem
from darjeeling.snippet import SnippetDatabase
from darjeeling.candidate import all_single_edit_patches
from darjeeling.transformation import find_all as find_all_transformations
import darjeeling.transformation
from darjeeling.transformation import Transformation, DeleteStatement, \
    PrependStatement, ReplaceStatement
from darjeeling.searcher import Searcher
from darjeeling.settings import Settings as RepairSettings
from darjeeling.exceptions import NoImplicatedLines

from .localize import localize
from .snapshot import Snapshot
from .analyze import Analysis

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


def sample(localization,    # type: Localization
           grouped          # type: Dict[FileLine, Dict[Type[Transformation], Transformation]]
           ):               # type: (...) -> Iterator[Transformation]:
    while True:
        line = localization.sample()
        # logger.debug("finding transformation at line: %s", line)

        if line not in grouped:
            try:
                localization = localization.without(line)
                continue
            except NoImplicatedLines:
                return

        transformations_by_schema = grouped[line]

        if not transformations_by_schema:
            # logger.debug("no transformations left at %s", line)
            del grouped[line]
            try:
                localization = localization.without(line)
            except NoImplicatedLines:
                # logger.debug("no transformations left in search space")
                raise StopIteration
            continue

        # prioritise deletion
        if DeleteStatement in transformations_by_schema:
            schema = DeleteStatement
        else:
            schema = random.choice(list(transformations_by_schema.keys()))

        transformations = transformations_by_schema[schema]
        # logger.debug("generating transformation using %s at %s",
        #              schema.__name__, line)

        # attempt to fetch the next transformation for the line and schema
        # if none are left, we remove the schema choice
        try:
            t = transformations.pop()
            # logger.debug("sampled transformation: %s", t)
            yield t
        except IndexError:
            # logger.debug("no %s left at %s", schema.__name__, line)
            try:
                del transformations_by_schema[schema]
                # logger.debug("removed entry for schema %s at line %s",
                #          schema.__name__, line)
            except Exception:
                # logger.exception(
                #     "failed to remove entry for %s at %s.\nchoices: %s",
                #     schema.__name__, line,
                #     [s.__name__ for s in transformations_by_schema.keys()])
                raise


def transformations(problem,        # type: Problem
                    snapshot,       # type: Snapshot
                    coverage,       # type: TestSuiteCoverage
                    localization,   # type: Localization
                    snippets,       # type: SnippetDatabase
                    analysis,       # type: Analysis,
                    settings        # type: RepairSettings
                    ):              # type: (...) -> List[Transformation]
    """
    Returns a list of all transformations for a given snapshot.
    """
    schemas = [PrependStatement, ReplaceStatement, DeleteStatement]
    lines = list(localization)  # type: List[FileLine]
    transformations = list(find_all_transformations(problem,
                                                    lines,
                                                    snippets,
                                                    schemas))

    # group transformations by line and type
    grouped = {}  # type: Dict[FileLine, Dict[Type[Transformation], Transformation]]  # noqa: pycodestyle
    for t in transformations:
        line = t.line
        if line not in grouped:
            grouped[line] = {}
        at_line = grouped[line]  # type: Dict[Type[Transformation], Transformation]  # noqa: pycodestyle

        schema = t.__class__
        if schema not in at_line:
            at_line[schema] = []
        at_line[schema].append(t)

    transformations = list(sample(localization, grouped))
    return transformations


def search(problem,                 # type: Problem
           snapshot,                # type: Snapshot
           localization,            # type: Localization
           coverage,                # type: TestSuiteCoverage
           analysis,                # type: Analysis
           transformations,         # type: List[Transformation]
           threads=1,               # type: int
           candidate_limit=None,    # type: Optional[int]
           time_limit_mins=None     # type: Optional[float]
           ):                       # type: (...) -> None
    if time_limit_mins:
        logger.debug("time limit for search process: %d minutes",
                     time_limit_mins)
        time_limit = timedelta(minutes=time_limit_mins)
    else:
        logger.debug("no time limit specified")
        time_limit = None

    if candidate_limit:
        logger.debug("candidate limit: %d candidates", candidate_limit)
    else:
        logger.debug("no candidate limit specified")

    candidates = all_single_edit_patches(transformations)
    search = Searcher(bugzoo=problem.bugzoo,
                      problem=problem,
                      candidates=candidates,
                      threads=threads,
                      candidate_limit=candidate_limit,
                      time_limit=time_limit)
    return search
