# -*- coding: utf-8 -*-

import threading

from tests.base import *

from radish.runner import Runner
from radish.feature import Feature
from radish.scenario import Scenario
from radish.stepmodel import Step
from radish.main import setup_config


class RunnerTestCase(RadishTestCase):
    """
        Tests for the runner class
    """
    @classmethod
    def setUpClass(cls):
        """
            Setup config object
        """
        setup_config({
            "--early_exit": False,
            "--debug-steps": False,
            "--debug-after-failure": False,
            "--inspect-after-failure": False,
            "--bdd-xml": False,
            "--no-ansi": False,
            "--no-line-jump": False,
            "--write-steps-once": False,
            "--scenarios": None,
            "--shuffle": False,
            "--write-ids": False,
            "--tags": None,
            "--expand": True,
        })

    def test_running_a_step(self):
        """
            Test running a step
        """
        data = threading.local()
        data.step_was_called = False

        def some_step(step):
            data.step_was_called = True

        step = Step(1, "Some step", "somefile.feature", 3, None, True)
        step.definition_func = some_step
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (tuple(), {})
        step.argument_match = argument_match_mock

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        returncode = runner.run_step(step)
        returncode.should.be.equal(0)
        step.state.should.be.equal(Step.State.PASSED)
        data.step_was_called.should.be.true

    def test_running_a_scenario(self):
        """
            Test running a scenario
        """
        data = threading.local()
        data.step_was_called = False

        def some_step(step):
            data.step_was_called = True

        step = Step(1, "Some step", "somefile.feature", 3, None, True)
        step.definition_func = some_step
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (tuple(), {})
        step.argument_match = argument_match_mock

        scenario = Scenario(1, 1, "Scenario", "Some scenario", "somefile.feature", 2, None)
        scenario.steps.append(step)

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        returncode = runner.run_scenario(scenario)
        returncode.should.be.equal(0)
        step.state.should.be.equal(Step.State.PASSED)
        data.step_was_called.should.be.true

    def test_running_a_feature(self):
        """
            Test running a feature
        """
        data = threading.local()
        data.step_was_called = False

        def some_step(step):
            data.step_was_called = True

        feature = Feature(1, "Feature", "Some feature", "somefile.feature", 1)

        scenario = Scenario(1, 1, "Scenario", "Some scenario", "somefile.feature", 2, feature)
        feature.scenarios.append(scenario)

        step = Step(1, "Some step", "somefile.feature", 3, scenario, True)
        step.definition_func = some_step
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (tuple(), {})
        step.argument_match = argument_match_mock
        scenario.steps.append(step)

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        runner.run_feature(feature)
        step.state.should.be.equal(Step.State.PASSED)
        data.step_was_called.should.be.true

    def test_running_all(self):
        """
            Test running a all features
        """
        data = threading.local()
        data.step_was_called = False

        def some_step(step):
            data.step_was_called = True

        feature = Feature(1, "Feature", "Some feature", "somefile.feature", 1)

        scenario = Scenario(1, 1, "Scenario", "Some scenario", "somefile.feature", 2, feature)
        feature.scenarios.append(scenario)

        step = Step(1, "Some step", "somefile.feature", 3, scenario, True)
        step.definition_func = some_step
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (tuple(), {})
        step.argument_match = argument_match_mock
        scenario.steps.append(step)

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        runner.start([feature], None)
        step.state.should.be.equal(Step.State.PASSED)
        data.step_was_called.should.be.true

    def test_returncode_of_runner(self):
        """
            Test returncode of run functions in Runner
        """
        def some_passed_step(step):
            pass

        def some_failed_step(step):
            raise AttributeError("I expect this error to test the behavior of a failed step")

        feature = Feature(1, "Feature", "Some feature", "somefile.feature", 1)

        scenario = Scenario(1, 1, "Scenario", "Some scenario", "somefile.feature", 2, feature)
        feature.scenarios.append(scenario)

        step1 = Step(1, "Some passed step", "somefile.feature", 3, scenario, True)
        step1.definition_func = some_passed_step
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (tuple(), {})
        step1.argument_match = argument_match_mock
        scenario.steps.append(step1)

        step2 = Step(2, "Some failed step", "somefile.feature", 4, scenario, True)
        step2.definition_func = some_failed_step
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (tuple(), {})
        step2.argument_match = argument_match_mock
        scenario.steps.append(step2)

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        returncode = runner.run_feature(feature)
        returncode.should.be.equal(1)
        step1.state.should.be.equal(Step.State.PASSED)
        step2.state.should.be.equal(Step.State.FAILED)
        scenario.state.should.be.equal(Step.State.FAILED)
        feature.state.should.be.equal(Step.State.FAILED)
