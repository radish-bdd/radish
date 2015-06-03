# -*- coding: utf-8 -*-

from tests.base import *

from radish.step import step, given, then
from radish.stepregistry import StepRegistry
from radish.exceptions import StepRegexError


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

    def test_registering_errornous_step_with_decorator(self):
        """
            Test registering a step with an invalid regex over decorator
        """
        def step_a():
            pass

        step("[[").when.called_with(step_a).should.throw(StepRegexError, "Cannot compile regex '[[' from step 'step_a': unexpected end of regular expression")

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

        given(r"I have the number \d+")(step_given)
        registry.steps.should.have.length_of(1)
        registry.steps[r"Given I have the number \d+"] = step_given

        # cannot test the when function because sure overwrites it!
        # stupid stuff
        # step_when(r"I add \d+ to my number")(step_when)
        # registry.steps.should.have.length_of(2)
        # registry.steps[r"When I add \d+ to my number"] = step_when

        then(r"I expect my number to be \d+")(step_then)
        registry.steps.should.have.length_of(2)
        registry.steps[r"Then I expect my number to be \d+"] = step_then
