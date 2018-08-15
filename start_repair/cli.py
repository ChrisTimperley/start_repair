import argparse
import os
import logging

from start_core.scenario import Scenario
from start_core.exceptions import STARTException
from start_image.name import name as name_image
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.language import Language
from bugzoo.core.test import TestSuite
from bugzoo.compiler import WafCompiler


logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)

DESCRIPTION = """
START [Repair]
""".strip()


# type: (str, int, int, float, bool, bool) -> Snapshot
def build_snapshot(filename,
                   timeout_mission,
                   timeout_liveness,
                   speedup,
                   check_waypoints,
                   use_oracle_workaround):
    logger.info("loading scenario from file [%s]", args.filename)
    scenario = Scenario.from_file(filename)
    logger.info("loaded scenario [%s]", scenario.name)

    logger.debug("constructing test suite")
    logger.debug("computing test command")
    cmd_test = 'python test.py test __ID__ --speedup {} --time-limit {} --liveness-timeout {}'
    cmd_test = cmd_test.format(speedup, timeout_mission, timeout_liveness)
    if check_waypoints:
        cmd_test += ' --check-wps'
    if not use_oracle_workaround:
        cmd_test += ' --no-workaround'
    logger.debug("computed test command: %s", cmd_test)

    def build_test(name, should_pass):
        return {'name': name,
                'command': cmd_test.replace('__ID__', name),
                'expected-outcome': should_pass,
                'kill-after': 15,
                'time-limit': timeout_mission + 30}
    jsn_test_suite = {
        'context': '/opt/ardupilot',
        'tests': [build_test('p1', True),
                  build_test('n1', False)]}
    test_suite = TestSuite.from_dict(jsn_test_suite)
    logger.debug("constructed test suite")

    name_snapshot = "start:{}".format(scenario.name)
    snapshot = Snapshot(name=name_snapshot,
                        image=name_image(scenario),
                        dataset="start",
                        program="ardupilot",
                        source=None,
                        source_dir="/opt/ardupilot",
                        languages=[Language.CPP],
                        harness=test_suite,
                        compiler=WafCompiler(time_limit=300.0),
                        files_to_instrument=[
                            'APMrover2/APMrover2.cpp',
                            'ArduCopter/ArduCopter.cpp',
                            'ArduPlane/ArduPlane.cpp'
                        ])

    return snapshot


def main():  # type: () -> None
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    subparsers = parser.add_subparsers()

    # - validate
    # - localize
    # - analyze
    # - repair

    cmd = subparsers.add_parser('validate',
        help='ensures that the program for a given experiment behaves as expected.')
    def cmd_validate(args):
        snapshot = build_snapshot(args.filename, args.timeout, args.speedup)

    cmd.set_defaults(func=cmd_validate)
    cmd.add_argument('filename',
                     help="the path to the scenario's configuration file.")
    cmd.add_argument('--debug',
                     help="prints debugging information to the stdout.",
                     action='store_true')

    log_to_stdout_formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s: %(message)s',
        '%Y-%m-%d %H:%M:%S')
    log_to_stdout = logging.StreamHandler()
    log_to_stdout.setLevel(logging.INFO)
    log_to_stdout.setFormatter(log_to_stdout_formatter)
    logging.getLogger('start_repair').addHandler(log_to_stdout)

    try:
        args = parser.parse_args()
        if args.debug:
            log_to_stdout.setLevel(logging.DEBUG)
        args.func(args)
    except STARTException as e:
        logger.exception("An error occurred during command execution: %s", e)
    except:
        logger.exception("An unexpected error occurred during command execution.")
        raise
