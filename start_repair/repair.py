
from bugzoo.core.coverage import TestSuiteCoverage
from bugzoo.manager import BugZoo
from start_core.scenario import Scenario
from darjeeling.localization import Localization
from darjeeling.problem import Problem
from darjeeling.snippet import SnippetDatabase
from darjeeling.transformation import find_all as find_all_transformations
from darjeeling.transformation import Transformation, \
                                      InsertStatement

from .localize import localize
from .snapshot import Snapshot
from .analyze import Analysis


def transformations(snapshot,   # type: Snapshot
                    coverage,   # type: TestSuiteCoverage
                    snippets,   # type: SnippetDatabase
                    analysis    # type: Analysis
                    ):          # type: (...) -> List[Transformation]
    """
    Returns a list of all transformations for a given snapshot.
    """
    client_bugzoo = BugZoo()
    client_bugzoo.bugs.add(snapshot)  # FIXME this is an annoying hack
    problem = Problem(client_bugzoo, snapshot, coverage, analysis=analysis)
    schemas = [InsertStatement]
    lines = list(coverage.failing.lines)
    transformations = list(find_all_transformations(problem,
                                                    lines,
                                                    snippets,
                                                    schemas))
    return transformations


def repair(snapshot,            # type: Snapshot
           localization,        # type: Localization
           coverage,            # type: TestSuiteCoverage
           analysis,            # type: Analysis
           transformations,     # type: List[Transformation]
           threads,             # type: int
           candidate_limit,     # type: Optional[int]
           time_limit_mins      # type: Optional[float]
           ):                   # type: (...) -> None
    client_bugzoo = BugZoo()
    client_bugzoo.bugs.add(snapshot)
    problem = Problem(bugzoo, snapshot, coverage, analysis=analysis)

    time_limit = None
    candidates = all_single_edit_patches(transformations)
    search = Searcher(bugzoo=client_bugzoo,
                      problem=problem,
                      candidates=candidates,
                      threads=threads,
                      candidate_limit=candidate_limit,
                      time_limit=time_limit)
