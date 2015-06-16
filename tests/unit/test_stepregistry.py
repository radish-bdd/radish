# -*- coding: utf-8 -*-

from tests.base import *

from radish.stepregistry import StepRegistry
from radish.exceptions import SameStepError


class StepRegistryTestCase(RadishTestCase):
    """
        Tests for the StepRegistry class
    """
    def test_registering_steps(self):
        """
            Test registering multiple steps
        """
        registry = StepRegistry()
        registry.steps.should.be.empty

        def step_a():
            pass

        def step_b():
            pass

        registry.register("abc", step_a)
        registry.steps.should.have.length_of(1)
        registry.steps["abc"].should.be.equal(step_a)

        registry.register("def", step_b)
        registry.steps.should.have.length_of(2)
        registry.steps["def"].should.be.equal(step_b)

    def test_registering_same_step(self):
        """
            Test registering step with same regex
        """
        registry = StepRegistry()
        registry.steps.should.be.empty

        def step_a():
            pass

        def step_b():
            pass

        registry.register("abc", step_a)
        registry.steps.should.have.length_of(1)
        registry.steps["abc"].should.be.equal(step_a)

        registry.register.when.called_with("abc", step_b).should.throw(SameStepError, "Cannot register step step_b with regex 'abc' because it is already used by step step_a")

        registry.steps.should.have.length_of(1)
        registry.steps["abc"].should.be.equal(step_a)

    def test_registering_object(self):
        """
            Test registering object as steps
        """
        registry = StepRegistry()
        registry.steps.should.be.empty

        class MySteps(object):
            ignore = ["no_step_method"]

            def some_step(step):
                """When I call some step"""

            def some_other_step(step):
                """
                    Then I expect some behaviour
                """

            def no_step_method(data):
                """
                    This is not a step method
                """

        steps_object = MySteps()
        registry.register_object(steps_object)

        registry.steps.should.have.length_of(2)
        registry.steps["When I call some step"].should.be.equal(steps_object.some_step)
        registry.steps["Then I expect some behaviour"].should.be.equal(steps_object.some_other_step)
