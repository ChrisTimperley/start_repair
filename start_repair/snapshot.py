__all__ = ['Snapshot']

from start_core.scenario import Scenario
from bugzoo.core.bug import Bug as BugZooSnapshot
from bugzoo.core.language import Language
from bugzoo.core.test import TestSuite
from bugzoo.compiler import WafCompiler


class Snapshot(BugZooSnapshot):
    # type: (Scenario, int, int, float, bool, bool) -> Snapshot
    @staticmethod
    def build(scenario,
              timeout_mission,
              timeout_liveness,
              speedup,
              check_waypoints,
              use_oracle_workaround):
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
