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
            "--write-steps-once": False,
            "--scenarios": None,
            "--shuffle": False,
            "--write-ids": False,
            "--feature-tags": None,
            "--scenario-tags": None
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
        step.arguments = tuple()
        step.keyword_arguments = {}

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

        step = Step(1, "Some step", "somefile.feature", 3, None, True)
        step.definition_func = some_step
        step.arguments = tuple()
        step.keyword_arguments = {}

        scenario = Scenario(1, 1, "Scenario", "Some scenario", "somefile.feature", 2, None)
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

        feature = Feature(1, "Feature", "Some feature", "somefile.feature", 1)

        scenario = Scenario(1, 1, "Scenario", "Some scenario", "somefile.feature", 2, feature)
        feature.scenarios.append(scenario)

        step = Step(1, "Some step", "somefile.feature", 3, scenario, True)
        step.definition_func = some_step
        step.arguments = tuple()
        step.keyword_arguments = {}
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
        step.arguments = tuple()
        step.keyword_arguments = {}
        scenario.steps.append(step)

        hook_mock = Mock()
        hook_mock.call.return_value = True
        runner = Runner(hook_mock)
        runner.start([feature], None)
        step.state.should.be.equal(Step.State.PASSED)
        data.step_was_called.should.be.true
