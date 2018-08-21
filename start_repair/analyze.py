from typing import Optional

from bugzoo.manager import BugZoo as BugZooClient  # FIXME temporary hack
from kaskara.analysis import Analysis

from .snapshot import Snapshot


def analyze(snapshot,           # type: Snapshot
            client_bugzoo=None  # type: Optional[BugZooClient]
            ):                  # type: (...) -> Analysis
    # TODO compute list of files
    analysis = Analysis.build(client_bugzoo, snapshot, files)
