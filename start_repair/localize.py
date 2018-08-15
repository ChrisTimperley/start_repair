__all__ = ['localize']

import logging
import json

from bugzoo.manager import BugZoo

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


def coverage(snapshot, fn_out='coverage.json'):
    bz = BugZoo()
    bz.bugs.add(snapshot)
    container = None
    try:
        container = bz.containers.provision(snapshot)
        logger.info("computing coverage")
        coverage = bz.containers.coverage(container)
        logger.info("computed coverage")

        # FIXME sanity check coverage!

        jsn = coverage.to_dict()
        logger.info("saving coverage to disk: %s", fn_out)
        with open(fn_out, 'w') as f:
            json.dump(jsn, f)
        logger.info("saved coverage to disk: %s", fn_out)
        return coverage
    finally:
        if container:
            del bz.containers[container.uid]
