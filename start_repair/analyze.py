from typing import Optional
import logging

from bugzoo.manager import BugZoo as BugZooClient  # FIXME temporary hack
from kaskara.analysis import Analysis

from .snapshot import Snapshot

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


def analyze(snapshot):  # type: (Snapshot) -> Analysis
    client_bugzoo = BugZooClient()
    client_bugzoo.bugs.add(snapshot)

    # FIXME fetch a list of files
    files = ['/opt/ardupilot/libraries/GCS_MAVLink/GCS_Param.cpp']

    logger.debug("performing analysis of snapshot: %s", snapshot)
    analysis = Analysis.build(client_bugzoo, snapshot, files)
    logger.debug("performed analysis of snapshot")
    return analysis
