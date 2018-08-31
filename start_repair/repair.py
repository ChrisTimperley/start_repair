__all__ = ['transformations', 'search']

from datetime import timedelta
import logging

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
from darjeeling.transformation import Transformation
from darjeeling.searcher import Searcher

from .localize import localize
from .snapshot import Snapshot
from .analyze import Analysis

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


def transformations(snapshot,       # type: Snapshot
                    coverage,       # type: TestSuiteCoverage
                    localization,   # type: Localization
                    snippets,       # type: SnippetDatabase
                    analysis        # type: Analysis
                    ):              # type: (...) -> List[Transformation]
    """
    Returns a list of all transformations for a given snapshot.
    """
    client_bugzoo = BugZoo()
    client_bugzoo.bugs.add(snapshot)  # FIXME this is an annoying hack
    problem = Problem(client_bugzoo, snapshot, coverage, analysis=analysis)
    schemas = [darjeeling.transformation.PrependStatement,
               darjeeling.transformation.ReplaceStatement,
               darjeeling.transformation.DeleteStatement]
    lines = list(localization)  # type: List[FileLine]
    transformations = list(find_all_transformations(problem,
                                                    lines,
                                                    snippets,
                                                    schemas))
    return transformations


def search(snapshot,                # type: Snapshot
           localization,            # type: Localization
           coverage,                # type: TestSuiteCoverage
           analysis,                # type: Analysis
           transformations,         # type: List[Transformation]
           threads=1,               # type: int
           candidate_limit=None,    # type: Optional[int]
           time_limit_mins=None     # type: Optional[float]
           ):                       # type: (...) -> None
    client_bugzoo = BugZoo()
    client_bugzoo.bugs.add(snapshot)
    problem = Problem(client_bugzoo, snapshot, coverage, analysis=analysis)

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
    search = Searcher(bugzoo=client_bugzoo,
                      problem=problem,
                      candidates=candidates,
                      threads=threads,
                      candidate_limit=candidate_limit,
                      time_limit=time_limit)
    return search
