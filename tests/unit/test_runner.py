# -*- coding: utf-8 -*-

import threading

from tests.base import *

from radish.core import Runner
from radish.feature import Feature
from radish.scenario import Scenario
from radish.step import Step
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
            "--write-steps-once": False
        })

    def test_running_a_step(self):
        """
            Test running a step
        """
        data = threading.local()
        data.step_was_called = False

        def some_step(step):
            data.step_was_called = True

        match_mock = Mock()
        match_mock.groupdict.return_value = None
        match_mock.groups.return_value = tuple()

        step = Step(1, "Some step", "somefile.feature", 3, None, False)
        step.definition_func = some_step
        step.arguments = match_mock

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        runner.run_step(step)
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

        match_mock = Mock()
        match_mock.groupdict.return_value = None
        match_mock.groups.return_value = tuple()

        step = Step(1, "Some step", "somefile.feature", 3, None, False)
        step.definition_func = some_step
        step.arguments = match_mock

        scenario = Scenario(1, "Scenario", "Some scenario", "somefile.feature", 2, None)
        scenario.steps.append(step)

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        runner.run_scenario(scenario)
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

        match_mock = Mock()
        match_mock.groupdict.return_value = None
        match_mock.groups.return_value = tuple()

        feature = Feature(1, "Feature", "Some feature", "somefile.feature", 1)

        scenario = Scenario(1, "Scenario", "Some scenario", "somefile.feature", 2, feature)
        feature.scenarios.append(scenario)

        step = Step(1, "Some step", "somefile.feature", 3, scenario, False)
        step.definition_func = some_step
        step.arguments = match_mock
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

        match_mock = Mock()
        match_mock.groupdict.return_value = None
        match_mock.groups.return_value = tuple()

        feature = Feature(1, "Feature", "Some feature", "somefile.feature", 1)

        scenario = Scenario(1, "Scenario", "Some scenario", "somefile.feature", 2, feature)
        feature.scenarios.append(scenario)

        step = Step(1, "Some step", "somefile.feature", 3, scenario, False)
        step.definition_func = some_step
        step.arguments = match_mock
        scenario.steps.append(step)

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        runner.start([feature], None)
        step.state.should.be.equal(Step.State.PASSED)
        data.step_was_called.should.be.true
