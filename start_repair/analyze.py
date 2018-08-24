from typing import Optional, List
import logging

from bugzoo.manager import BugZoo as BugZooClient  # FIXME temporary hack
from kaskara.analysis import Analysis

from .snapshot import Snapshot

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


def analyze(snapshot,   # type: Snapshot
            files       # type: List[str]
            ):          # type: (...) -> Analysis
    logger.debug("performing analysis of snapshot: %s", snapshot)
    client_bugzoo = BugZooClient()
    client_bugzoo.bugs.add(snapshot)
    analysis = Analysis.build(client_bugzoo, snapshot, files)
    logger.debug("performed analysis of snapshot")
    return analysis
