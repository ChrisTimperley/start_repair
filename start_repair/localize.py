__all__ = ['localize']

import logging
import json

from bugzoo.manager import BugZoo
from bugzoo.core.coverage import TestSuiteCoverage
from start_core.exceptions import UnexpectedTestOutcome
from darjeeling.localization import Localization

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


def metric(ep, np, ef, nf):
    # type: (int, int, int, int) -> float
    return 1.0 if ep == 0 and nf == 0 else 0.0


def localize(coverage):
    # type: (TestSuiteCoverage) -> Localization
    return Localization.from_coverage(coverage, metric)


def coverage(snapshot, fn_out='coverage.json'):
    bz = BugZoo()
    bz.bugs.add(snapshot)
    container = None
    try:
        container = bz.containers.provision(snapshot)
        logger.info("computing coverage")
        coverage = bz.containers.coverage(container)
        logger.info("computed coverage")

        for test in snapshot.tests:
            actual_outcome = coverage[test.name].outcome.passed
            expected_outcome = test.expected_outcome
            if actual_outcome != expected_outcome:
                msg = "unexpected test outcome when computing coverage for test [%s]: ('%s' should be '%s')."
                msg = msg.format(test.name,
                                 'PASS' if actual_outcome else 'FAIL',
                                 'PASS' if expected_outcome else 'FAIL')
                raise UnexpectedTestOutcome(msg)

        # restrict coverage to .cpp files
        covered_files = [fn for fn in coverage.lines.files if fn.endswith('.cpp')]
        covered_files = [fn for fn in covered_files \
                         if not fn.startswith('libraries/SITL')]
        coverage = coverage.restricted_to_files(covered_files)

        jsn = coverage.to_dict()
        logger.info("saving coverage to disk: %s", fn_out)
        with open(fn_out, 'w') as f:
            json.dump(jsn, f)
        logger.info("saved coverage to disk: %s", fn_out)
        return coverage
    finally:
        if container:
            del bz.containers[container.uid]
