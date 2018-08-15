import argparse
import os
import logging

from start_core.scenario import Scenario
from start_core.exceptions import STARTException
from bugzoo.manager import BugZoo

from .snapshot import Snapshot
from .validate import validate


logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)

DESCRIPTION = """
START [Repair]
""".strip()


# type: (str) -> Scenario
def load_scenario(filename):
    logger.info("loading scenario from file [%s]", filename)
    scenario = Scenario.from_file(filename)
    logger.info("loaded scenario [%s] from file", scenario.name)
    return scenario


def add_debug_option(parser):
    parser.add_argument('--debug',
                        help="prints debugging information to the stdout.",
                        action='store_true',
                        default=False)


def add_mission_options(parser):
    parser.add_argument('--timeout',
                        help="the number of seconds that may pass without success until a mission is considered a failure.",
                        type=int,
                        default=300)
    parser.add_argument('--timeout-liveness',
                        help="the number of seconds that may pass without communication with the rover until the mission is aborted.",
                        type=int,
                        default=30.0)
    parser.add_argument('--speedup',
                        help="the speed-up factor that should be applied to the simulation clock.",
                        type=float,
                        default=10.0)


def cmd_localize(args):
    logger.info("performing fault localization for scenario")

    fn_out = "coverage.json"

    logger.info("saved fault localization to disk: %s", fn_out)


# FIXME where should we save the patch?
def cmd_repair(args):
    scenario = load_scenario(args.filename)
    logger.info("repairing scenario")

    logger.info("successfully repaired scenario")


def cmd_validate(args):
    scenario = load_scenario(args.filename)
    logger.info("validating scenario")
    snapshot = Snapshot.build(scenario=scenario,
                              timeout_mission=args.timeout,
                              timeout_liveness=args.timeout_liveness,
                              speedup=args.speedup,
                              check_waypoints=True,  # FIXME
                              use_oracle_workaround=False)  # FIXME
    validate(snapshot)
    logger.info("validated scenario")


def cmd_analyze(args):
    logger.info("loading scenario from file [%s]", args.filename)
    scenario = Scenario.from_file(args.filename)
    logger.info("loaded scenario [%s] from file", scenario.name)
    logger.info("performing static analyis of scenario")

    fn_out = "analysis.json"

    logger.info("saved static analysis to disk: %s", fn_out)


def main():  # type: () -> None
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    subparsers = parser.add_subparsers()

    # [validate]
    cmd = subparsers.add_parser('validate',
        help='ensures that a given scenario behaves as expected.')
    cmd.add_argument('filename',
                     help="the path to the scenario configuration file.")
    add_mission_options(cmd)
    add_debug_option(cmd)
    cmd.set_defaults(func=cmd_validate)

    # [localize]
    cmd = subparsers.add_parser('localize',
        help='performs fault localization for a given scenario.')
    cmd.add_argument('filename',
                     help="the path to the scenario configuration file.")
    add_mission_options(cmd)
    add_debug_option(cmd)
    cmd.set_defaults(func=cmd_localize)

    # [analyze]
    cmd = subparsers.add_parser('analyze',
        help='performs static analysis of a given scenario.')
    cmd.add_argument('filename',
                     help="the path to the scenario configuration file.")
    add_debug_option(cmd)
    cmd.set_defaults(func=cmd_analyze)

    # [repair]
    cmd = subparsers.add_parser('repair',
        help='attempts to repair the source code for a given scenario.')
    cmd.add_argument('filename',
                     help="the path to the scenario configuration file.")
    add_mission_options(cmd)
    add_debug_option(cmd)
    cmd.set_defaults(func=cmd_repair)

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
