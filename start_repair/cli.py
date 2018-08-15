import argparse
import os
import logging

from start_core.scenario import Scenario
from start_core.exceptions import STARTException
from start_image.name import name as name_image

from .snapshot import Snapshot


logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)

DESCRIPTION = """
START [Repair]
""".strip()


def main():  # type: () -> None
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    subparsers = parser.add_subparsers()

    # - validate
    # - localize
    # - analyze
    # - repair

    cmd = subparsers.add_parser('validate',
        help='ensures that a given scenario behaves as expected.')
    cmd.add_argument('filename',
                     help="the path to the scenario's configuration file.")
    cmd.add_argument('--timeout',
                     help="the number of seconds that may pass without success until a mission is considered a failure.",
                     type=int,
                     default=300)
    cmd.add_argument('--timeout-liveness',
                     help="the number of seconds that may pass without communication with the rover until the mission is aborted.",
                     type=int,
                     default=30.0)
    cmd.add_argument('--speedup',
                     help="the speed-up factor that should be applied to the simulation clock.",
                     type=float,
                     default=10.0)
    cmd.add_argument('--debug',
                     help="prints debugging information to the stdout.",
                     action='store_true',
                     default=False)
    def cmd_validate(args):
        snapshot = Snapshot.build(args.filename, args.timeout, args.speedup)
        logger.info("validated scenario: %s", snapshot.name)  # FIXME
    cmd.set_defaults(func=cmd_validate)

    log_to_stdout_formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s: %(message)s',
        '%Y-%m-%d %H:%M:%S')
    log_to_stdout = logging.StreamHandler()
    log_to_stdout.setLevel(logging.INFO)
    log_to_stdout.setFormatter(log_to_stdout_formatter)
    logging.getLogger('start_repair').addHandler(log_to_stdout)

    try:
        args = parser.parse_args()
        if hasattr(args, 'debug') and args.debug:
            log_to_stdout.setLevel(logging.DEBUG)
        if hasattr(args, 'func'):
            args.func(args)
    except SystemExit:
        pass
    except STARTException as e:
        logger.exception("An error occurred during command execution: %s", e)
    except:
        logger.exception("An unexpected error occurred during command execution.")
        raise
