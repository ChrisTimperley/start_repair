__all__ = ['validate']

import logging

from bugzoo.manager import BugZoo

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


def validate(snapshot):
    bz = BugZoo()
    bz.bugs.add(snapshot)
    container = None
    try:
        container = bz.containers.provision(snapshot)
        for test in snapshot.tests:
            logger.info("- executing test: %s [ACTUAL/EXPECTED]", test.name)
            outcome = bz.containers.test(container, test)  # FIXME add verbose option
            s_actual = "PASS" if outcome.passed else "FAIL"
            s_expected = "PASS" if test.expected_outcome else "FAIL"
            logger.info("- executed test: %s [%s/%s]",
                        test.name, s_actual, s_expected)
            if outcome.passed != test.expected_outcome:
                logger.error("unexpected outcome for test [%s]", test.name)
                raise SystemExit
    finally:
        if container:
            del bz.containers[container.uid]
