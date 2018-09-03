__all__ = ['Snapshot']

import logging

from start_core.scenario import Scenario
from start_image.name import name as name_image
from bugzoo.core.bug import Bug as BugZooSnapshot
from bugzoo.core.language import Language
from bugzoo.core.test import TestSuite
from bugzoo.compiler import SimpleCompiler

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


class Snapshot(BugZooSnapshot):
    # type: (Scenario, int, int, float, bool, bool) -> Snapshot
    @staticmethod
    def build(scenario,                 # type: Scenario
              timeout_mission,          # type: int
              timeout_liveness,         # type: int
              timeout_connection,       # type: int
              speedup,                  # type: int
              check_waypoints,          # type: bool
              use_oracle_workaround     # type: bool
              ):                        # type: (...) -> Snapshot
        logger.debug("constructing test suite")
        logger.debug("computing test command")
        cmd_test = 'start-cli --debug execute scenario.config'
        cmd_test += ' --speedup {}'.format(speedup)
        cmd_test += ' --timeout-connection {}'.format(timeout_connection)
        cmd_test += ' --time-limit {}'.format(timeout_mission)
        cmd_test += ' --timeout-liveness {}'.format(timeout_liveness)
        if not check_waypoints:
            cmd_test += ' --no-check-wps'
        if not use_oracle_workaround:
            cmd_test += ' --no-workaround'
        logger.debug("computed base test command: %s", cmd_test)

        def build_test(name, use_attack):
            command = cmd_test
            if use_attack:
                command += ' --attack'
            return {'name': name,
                    'command': command,
                    'expected-outcome': not use_attack,
                    'kill-after': 15,
                    'time-limit': timeout_mission + 30}
        jsn_test_suite = {
            'context': '/opt/ardupilot',
            'tests': [build_test('p1', False),
                      build_test('n1', True)]}
        test_suite = TestSuite.from_dict(jsn_test_suite)
        logger.debug("constructed test suite")
        name_snapshot = "start:{}".format(scenario.name)

        command_vehicle = {
            'APMrover2': 'rover',
            'ArduCopter': 'copter',
            'ArduPlane': 'plane'
        }[scenario.mission.vehicle]

        ldflags = "--coverage"
        cxxflags= "--coverage -Wno-error=maybe-uninitialized -save-temps=obj"
        configure = "./waf configure --no-submodule-update LDFLAGS='{}' CXXFLAGS='{}'"
        configure = configure.format(ldflags, cxxflags)
        cmdi =  "{} && ./waf {}".format(configure, command_vehicle)
        cmdi = cmdi.format(ldflags, cxxflags)
        compiler = SimpleCompiler(command='./waf {}'.format(command_vehicle),
                                  command_clean='./waf clean',
                                  command_with_instrumentation=cmdi,
                                  context='/opt/ardupilot',
                                  time_limit=300.0)

        snapshot = Snapshot(name=name_snapshot,
                            image=name_image(scenario),
                            dataset="start",
                            program="ardupilot",
                            source=None,
                            source_dir="/opt/ardupilot",
                            languages=[Language.CPP],
                            harness=test_suite,
                            compiler=compiler,
                            files_to_instrument=[
                                'APMrover2/APMrover2.cpp',
                                'ArduCopter/ArduCopter.cpp',
                                'ArduPlane/ArduPlane.cpp'
                            ])
        return snapshot
