# -*- coding: utf-8 -*-

import re
from tests.base import *

from radish.matcher import merge_steps, merge_step, match_step
from radish.feature import Feature
from radish.scenario import Scenario
from radish.stepmodel import Step
from radish.exceptions import StepDefinitionNotFoundError
from radish.main import setup_config


class MatcherTestCase(RadishTestCase):
    """
        Tests the Matcher class
    """

    @classmethod
    def setUpClass(cls):
        """
            Setup config object
        """
        setup_config({
            "--basedir": ['foo'],
        })

    def test_match_steps(self):
        """
            Test matching steps from feature files with registered steps
        """
        steps = {re.compile(r"Given I have the number (\d+)"): "some_func",
                 re.compile(r"I add (\d+) to my number"): "some_other_func"}

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

    def test_similar_steps_pattern(self):
        """
            Test matching steps from feature files with similar patterns
        """
        steps = {re.compile(r"Given I have the number (\d+)"): "some_func",
                 re.compile(r"Given I have the number (\d+) to add"): "some_other_func"}

        match, func = match_step("Given I have the number 5", steps)
        arguments, keyword_arguments = match.evaluate()
        arguments.should.be.equal(("5",))
        keyword_arguments.should.be.equal({})
        func.should.be.equal("some_func")

        match, func = match_step("Given I have the number 5 to add", steps)
        arguments, keyword_arguments = match.evaluate()
        arguments.should.be.equal(("5",))
        keyword_arguments.should.be.equal({})
        func.should.be.equal("some_other_func")

        match = match_step("Given I have the number", steps)
        match.should.be.none  # pylint: disable=pointless-statement

    def test_similar_steps(self):
        """
            Test matching steps from feature files with similar text
        """
        steps = {"This is a short sentence": "some_func",
                 "This is a short sentence with few more words": "some_other_func"}

        match, func = match_step("This is a short sentence", steps)
        arguments, keyword_arguments = match.evaluate()
        keyword_arguments.should.be.equal({})
        func.should.be.equal("some_func")

        match, func = match_step("This is a short sentence with few more words", steps)
        arguments, keyword_arguments = match.evaluate()
        keyword_arguments.should.be.equal({})
        func.should.be.equal("some_other_func")

        match = match_step("This is not a step", steps)
        match.should.be.none  # pylint: disable=pointless-statement

    def test_similar_steps_with_args(self):
        """
            Test matching steps from feature files with similar text and arguments
        """
        steps = {"This is a short {arg:S}": "some_func",
                 "This is a short {arg:S} with few more words": "some_other_func"}

        match, func = match_step("This is a short sentence", steps)
        arguments, keyword_arguments = match.evaluate()
        assert keyword_arguments["arg"] == "sentence"
        func.should.be.equal("some_func")

        match, func = match_step("This is a short sentence with few more words", steps)
        arguments, keyword_arguments = match.evaluate()
        assert keyword_arguments["arg"] == "sentence"
        func.should.be.equal("some_other_func")

        match = match_step("This is not a step", steps)
        match.should.be.none  # pylint: disable=pointless-statement

    def test_merge_steps(self):
        """
            Test merging steps from feature files with registered steps
        """
        steps = {re.compile(r"Given I have the number (\d+)"): "some_func",
                 re.compile(r"I add (\d+) to my number"): "some_other_func"}

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
        steps = {re.compile(r"Given I have the number (\d+)"): "some_func",
                 re.compile(r"I add (\d+) to my number"): "some_other_func"}

        feature = Feature(1, "Feature", "Some feature", "test.feature", 1)
        scenario = Scenario(1, "Scenario", "Adding numbers", "test.feature", 2, feature)
        scenario.steps.append(Step(1, "When I call a non-existing step", "test.feature", 3, scenario, False))
        feature.scenarios.append(scenario)

        merge_steps.when.called_with([feature], steps).should.throw(StepDefinitionNotFoundError)
