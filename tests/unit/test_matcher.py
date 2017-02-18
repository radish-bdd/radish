# -*- coding: utf-8 -*-

import re
from tests.base import *

from radish.matcher import merge_steps, merge_step, match_step
from radish.feature import Feature
from radish.scenario import Scenario
from radish.stepmodel import Step
from radish.exceptions import StepDefinitionNotFoundError


class MatcherTestCase(RadishTestCase):
    """
        Tests the Matcher class
    """
    def test_match_steps(self):
        """
            Test matching steps from feature files with registered steps
        """
        steps = {re.compile(r"Given I have the number (\d+)"): "some_func", re.compile(r"I add (\d+) to my number"): "some_other_func"}

        match, func = match_step("Given I have the number 5", steps)
        arguments, keyword_arguments = match.evaluate()
        arguments.should.be.equal(("5",))
        keyword_arguments.should.be.equal({})
        func.should.be.equal("some_func")

        match, func = match_step("When I add 2 to my number", steps)
        arguments, keyword_arguments = match.evaluate()
        arguments.should.be.equal(("2",))
        keyword_arguments.should.be.equal({})
        func.should.be.equal("some_other_func")

        match = match_step("when I call a non-existing step", steps)
        match.should.be.none  # pylint: disable=pointless-statement

    def test_merge_steps(self):
        """
            Test merging steps from feature files with registered steps
        """
        steps = {re.compile(r"Given I have the number (\d+)"): "some_func", re.compile(r"I add (\d+) to my number"): "some_other_func"}

        feature = Feature(1, "Feature", "Some feature", "test.feature", 1)
        scenario = Scenario(1, "Scenario", "Adding numbers", "test.feature", 2, feature)
        scenario.steps.append(Step(1, "Given I have the number 5", "test.feature", 3, scenario, False))
        scenario.steps.append(Step(2, "When I add 2 to my number", "test.feature", 4, scenario, False))
        feature.scenarios.append(scenario)

        merge_steps([feature], steps)

        scenario.steps[0].definition_func.should.be.equal("some_func")
        scenario.steps[0].argument_match.evaluate()[0].should.be.equal(("5",))
        scenario.steps[1].definition_func.should.be.equal("some_other_func")
        scenario.steps[1].argument_match.evaluate()[0].should.be.equal(("2",))

    def test_merge_non_existing_step(self):
        """
            Test merging non existing step
        """
        steps = {re.compile(r"Given I have the number (\d+)"): "some_func", re.compile(r"I add (\d+) to my number"): "some_other_func"}

        feature = Feature(1, "Feature", "Some feature", "test.feature", 1)
        scenario = Scenario(1, "Scenario", "Adding numbers", "test.feature", 2, feature)
        scenario.steps.append(Step(1, "When I call a non-existing step", "test.feature", 3, scenario, False))
        feature.scenarios.append(scenario)

        merge_steps.when.called_with([feature], steps).should.throw(StepDefinitionNotFoundError, "Cannot find step definition for step 'When I call a non-existing step' in test.feature:3")
