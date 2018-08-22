from bugzoo.core.fileline import FileLine
from bugzoo.core.coverage import TestSuiteCoverage
from bugzoo.manager import BugZoo
from start_core.scenario import Scenario
from darjeeling.snippet import SnippetDatabase
from darjeeling.transformation import find_all_transformations

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
    problem = Problem(client_bugzoo, snapshot, coverage, analysis=analysis)
    schemas = []
    transformations = list(find_all_transformations(problem, snippets, schemas))
    return transformations


def repair(scenario,            # type: Scenario
           coverage,            # type: TestSuiteCoverage
           analysis,            # type: Analysis
           snippets,            # type: SnippetDatabase
           threads,             # type: int
           candidate_limit,     # type: Optional[int]
           time_limit_mins      # type: Optional[float]
           ):                   # type: (...) -> None
    localization = localize(coverage)
    snapshot = Snapshot.build(scenario,
                              timeout_mission,
                              timeout_liveness,
                              timeout_connection,
                              speedup,
                              check_waypoints,
                              use_oracle_workaround)
    problem = Problem(bugzoo,
                      snapshot,
                      coverage,
                      analysis=analysis)

    # generate the search space
    schemes = []
    transformations = sample_by_localization_and_type(problem,
                                                      snippets,
                                                      localization,
                                                      schemas,
                                                      threads=threads,
                                                      eager=True)
    candidates = all_single_edit_patches(transformations)

    # repair
    time_limit = None
    search = Searcher(bugzoo=bz,
                      problem=problem,
                      candidates=candidates,
                      threads=threads,
                      candidate_limit=candidate_limit,
                      time_limit=time_limit)
