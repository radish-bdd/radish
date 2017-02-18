# -*- coding: utf-8 -*-

import re
import threading

from tests.base import *

from radish.stepmodel import Step
from radish.stepregistry import StepRegistry, step, given, then
from radish.exceptions import RadishError, StepRegexError


class StepTestCase(RadishTestCase):
    """
        Tests for the step functionality
    """
    def test_registering_steps_with_decorator(self):
        """
            Test registering steps with decorator
        """
        registry = StepRegistry()
        registry.steps.should.have.length_of(0)

        def step_a():
            pass

        def step_b():
            pass

        step("abc")(step_a)
        registry.steps.should.have.length_of(1)
        registry.steps["abc"].should.be.equal(step_a)

        step("def")(step_b)
        registry.steps.should.have.length_of(2)
        registry.steps["def"].should.be.equal(step_b)

    def test_registering_steps_with_gherkin_decorators(self):
        """
            Test registering steps with gherkin specific decorators
        """
        def step_given():
            pass

        def step_when():
            pass

        def step_then():
            pass

        registry = StepRegistry()
        registry.steps.should.be.empty

        given(r"I have the number {:g}")(step_given)
        registry.steps.should.have.length_of(1)
        registry.steps[r"Given I have the number {:g}"] = step_given

        # cannot test the when function because sure overwrites it!
        # stupid stuff
        # step_when(r"I add \d+ to my number")(step_when)
        # registry.steps.should.have.length_of(2)
        # registry.steps[r"When I add \d+ to my number"] = step_when

        then(re.compile(r"I expect my number to be \d+"))(step_then)
        registry.steps.should.have.length_of(2)

    def test_run_step_passed(self):
        """
            Test running a passing step
        """
        data = threading.local()
        data.step_was_run = False

        def step_passed(step):
            data.step_was_run = True

        step = Step(1, "I call a passing step", "somefile.feature", 3, None, True)
        step.definition_func = step_passed
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (re.search(step.sentence, step.sentence).groups(), {})
        step.argument_match = argument_match_mock

        step.state.should.be.equal(Step.State.UNTESTED)
        step.run.when.called_with().should.return_value(Step.State.PASSED)
        data.step_was_run.should.be.true

    def test_run_step_with_arguments_passed(self):
        """
            Test running a passing step with arguments
        """
        data = threading.local()
        data.step_was_run = False
        data.number = None
        data.string = None

        def step_passed(step, number, string):
            data.step_was_run = True
            data.number = int(number)
            data.string = string

        step = Step(1, "I call a passing step with number argument 42 and string argument 'Tschau'", "somefile.feature", 3, None, True)
        step.definition_func = step_passed
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (
            re.search(r"I call a passing step with number argument (\d+) and string argument '(.*?)'", step.sentence).groups(), {})
        step.argument_match = argument_match_mock

        step.state.should.be.equal(Step.State.UNTESTED)
        step.run.when.called_with().should.return_value(Step.State.PASSED)
        data.step_was_run.should.be.true
        data.number.should.be.equal(42)
        data.string.should.be.equal("Tschau")

    def test_run_step_with_keyword_arguments_passed(self):
        """
            Test running a passing step with keyword arguments
        """
        data = threading.local()
        data.step_was_run = False
        data.number = None
        data.string = None

        def step_passed(step, number, string):
            data.step_was_run = True
            data.number = int(number)
            data.string = string

        step = Step(1, "I call a passing step with string argument 'Tschau' and number argument 42", "somefile.feature", 3, None, True)
        step.definition_func = step_passed
        match = re.search("I call a passing step with string argument '(?P<string>.*?)' and number argument (?P<number>\d+)", step.sentence)
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (match.groups(), match.groupdict())
        step.argument_match = argument_match_mock

        step.state.should.be.equal(Step.State.UNTESTED)
        step.run.when.called_with().should.return_value(Step.State.PASSED)
        data.step_was_run.should.be.true
        data.number.should.be.equal(42)
        data.string.should.be.equal("Tschau")

    def test_run_step_failed(self):
        """
            Test running a failing step
        """
        data = threading.local()
        data.step_was_run = False

        def step_failed(step):
            data.step_was_run = True
            assert False, "This step fails by design"

        step = Step(1, "I call a failing step", "somefile.feature", 3, None, True)
        step.definition_func = step_failed
        argument_match_mock = Mock()
        argument_match_mock.evaluate.return_value = (re.search(step.sentence, step.sentence).groups(), {})
        step.argument_match = argument_match_mock

        step.state.should.be.equal(Step.State.UNTESTED)
        step.run.when.called_with().should.return_value(Step.State.FAILED)
        step.failure.shouldnt.be.none
        step.failure.reason.should.be.equal("This step fails by design")
        data.step_was_run.should.be.true

    def test_run_a_step_without_definition(self):
        """
            Test running a step without assining a definition
        """
        step = Step(1, "I call an invalid step", "somefile.feature", 3, None, True)
        step.run.when.called_with().should.throw(RadishError, "The step 'I call an invalid step' does not have a step definition")
