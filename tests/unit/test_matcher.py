# -*- coding: utf-8 -*-

from tests.base import *

from radish.matcher import Matcher
from radish.feature import Feature
from radish.scenario import Scenario
from radish.step import Step
from radish.exceptions import StepDefinitionNotFoundError


class MatcherTestCase(RadishTestCase):
    """
        Tests the Matcher class
    """
    def test_match_steps(self):
        """
            Test matching steps from feature files with registered steps
        """
        matcher = Matcher()
        steps = {r"Given I have the number (\d+)": "some_func", r"I add (\d+) to my number": "some_other_func"}

        arguments, func = matcher.match("Given I have the number 5", steps)
        arguments.groups().should.be.equal(("5",))
        func.should.be.equal("some_func")

        arguments, func = matcher.match("When I add 2 to my number", steps)
        arguments.groups().should.be.equal(("2",))
        func.should.be.equal("some_other_func")

        arguments, func = matcher.match("when I call a non-existing step", steps)
        arguments.should.be.none
        func.should.be.none

    def test_merge_steps(self):
        """
            Test merging steps from feature files with registered steps
        """
        matcher = Matcher()
        steps = {r"Given I have the number (\d+)": "some_func", r"I add (\d+) to my number": "some_other_func"}

        feature = Feature("Some feature", "test.feature", 1)
        scenario = Scenario("Adding numbers", "test.feature", 2)
        scenario.steps.append(Step("Given I have the number 5", "test.feature", 3))
        scenario.steps.append(Step("When I add 2 to my number", "test.feature", 4))
        feature.scenarios.append(scenario)

        matcher.merge_steps([feature], steps)

        scenario.steps[0].definition_func.should.be.equal("some_func")
        scenario.steps[0].arguments.groups().should.be.equal(("5",))
        scenario.steps[1].definition_func.should.be.equal("some_other_func")
        scenario.steps[1].arguments.groups().should.be.equal(("2",))

    def test_merge_non_existing_step(self):
        """
            Test merging non existing step
        """
        matcher = Matcher()
        steps = {r"Given I have the number (\d+)": "some_func", r"I add (\d+) to my number": "some_other_func"}

        feature = Feature("Some feature", "test.feature", 1)
        scenario = Scenario("Adding numbers", "test.feature", 2)
        scenario.steps.append(Step("When I call a non-existing step", "test.feature", 3))
        feature.scenarios.append(scenario)

        matcher.merge_steps.when.called_with([feature], steps).should.throw(StepDefinitionNotFoundError, "Cannot find step definition for step 'When I call a non-existing step' in test.feature:3")
