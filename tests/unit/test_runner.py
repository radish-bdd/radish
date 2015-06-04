# -*- coding: utf-8 -*-

import threading

from tests.base import *

from radish.core import Runner
from radish.feature import Feature
from radish.scenario import Scenario
from radish.step import Step


class RunnerTestCase(RadishTestCase):
    """
        Tests for the runner class
    """
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

        step = Step("Some step", "somefile.feature", 3)
        step.definition_func = some_step
        step.arguments = match_mock

        runner = Runner([])
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

        step = Step("Some step", "somefile.feature", 3)
        step.definition_func = some_step
        step.arguments = match_mock

        scenario = Scenario("Some scenario", "somefile.feature", 2)
        scenario.steps.append(step)

        runner = Runner([])
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

        step = Step("Some step", "somefile.feature", 3)
        step.definition_func = some_step
        step.arguments = match_mock

        scenario = Scenario("Some scenario", "somefile.feature", 2)
        scenario.steps.append(step)

        feature = Feature("Some feature", "somefile.feature", 1)
        feature.scenarios.append(scenario)

        runner = Runner([])
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

        step = Step("Some step", "somefile.feature", 3)
        step.definition_func = some_step
        step.arguments = match_mock

        scenario = Scenario("Some scenario", "somefile.feature", 2)
        scenario.steps.append(step)

        feature = Feature("Some feature", "somefile.feature", 1)
        feature.scenarios.append(scenario)

        runner = Runner([feature])
        runner.start()
        step.state.should.be.equal(Step.State.PASSED)
        data.step_was_called.should.be.true
