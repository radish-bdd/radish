# -*- coding: utf-8 -*-

"""
radish
~~~~~~

Behavior Driven Development tool for Python - the root from red to green

Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import re

import pytest

from radish.stepregistry import step, steps
from radish.stepregistry import given, when, then
from radish.compat import re_pattern
import radish.exceptions as errors


def test_registering_simple_steps(stepregistry):
    """
    Test registering simple Step functions
    """
    # given
    def step_a():
        pass

    def step_b():
        pass

    # when
    stepregistry.register("step_pattern_a", step_a)
    stepregistry.register("step_pattern_b", step_b)

    # then
    assert len(stepregistry.steps) == 2
    assert stepregistry.steps["step_pattern_a"] == step_a
    assert stepregistry.steps["step_pattern_b"] == step_b


def test_registering_step_pattern_twice(stepregistry):
    """
    Test registering the same Step pattern twice
    """
    # given
    def step_a():
        pass

    def step_b():
        pass

    stepregistry.register("step_pattern_a", step_a)

    # when
    with pytest.raises(errors.SameStepError) as exc:
        stepregistry.register("step_pattern_a", step_b)

    # then
    assert str(exc.value).startswith(
        "Cannot register step step_b with regex 'step_pattern_a' because it is already used by step step_a"
    )


def test_registering_steps_via_object(stepregistry):
    """
    Test registering Steps via object
    """
    # given
    class MySteps(object):
        def some_step(self):
            """When I call some step"""

        def some_other_step(self):
            """
            I do some stuff

            This is not part of the step pattern
            """

    # when
    steps_object = MySteps()
    stepregistry.register_object(steps_object)

    # then
    assert len(stepregistry.steps) == 2
    assert stepregistry.steps["When I call some step"] == steps_object.some_step
    assert stepregistry.steps["I do some stuff"] == steps_object.some_other_step


def test_ignore_methods_registering_object(stepregistry):
    """
    Test ignoring methods when registering an object
    """
    # given
    class MySteps(object):
        ignore = ["some_method"]

        def some_step(self):
            """When I call some step"""

        def some_method(self):
            pass

    # when
    steps_object = MySteps()
    stepregistry.register_object(steps_object)

    # then
    assert len(stepregistry.steps) == 1
    assert stepregistry.steps["When I call some step"] == steps_object.some_step


def test_error_if_no_step_regex_given_for_object(stepregistry):
    """
    Test error if a step method in object has no regex
    """
    # given
    class MySteps(object):
        def some_step(self):
            pass

    # when
    steps_object = MySteps()

    with pytest.raises(errors.RadishError) as exc:
        stepregistry.register_object(steps_object)

    # then
    assert (
        str(exc.value)
        == "Step definition 'some_step' from class must have step regex in docstring"
    )


def test_invalid_regex_step_pattern_in_method_docstring(stepregistry):
    """
    Test invalid regex Step pattern in method docstring
    """
    # given
    class MySteps(object):
        def some_step(self):
            """
            So (( invalid )(
            """

    # when
    steps_object = MySteps()

    with pytest.raises(errors.StepRegexError) as exc:
        stepregistry.register_object(steps_object)

    # then
    assert str(exc.value).startswith(
        "Cannot compile regex 'So (( invalid )(' from step"
    )


@pytest.mark.parametrize(
    "pattern",
    ["I do some stuff", re.compile("I do some stuff")],
    ids=["Step with Step Pattern", "Step with Regex"],
)
def test_registering_step_function_via_step_decorator(pattern, stepregistry):
    """
    Test registering Step function via step decorator
    """
    # given & when
    @step(pattern)
    def step_a(step):
        pass

    # then
    assert len(stepregistry.steps) == 1
    if not isinstance(pattern, re_pattern):  # doesn't work for re_pattern.
        assert stepregistry.steps[pattern] == step_a


@pytest.mark.parametrize(
    "pattern, expected_pattern",
    [
        ("I do some stuff", "Given I do some stuff"),
        (re.compile("I do some stuff"), re.compile("Given I do some stuff")),
    ],
    ids=["Step with Step Pattern", "Step with Regex"],
)
def test_registering_step_function_via_given_decorator(
    pattern, expected_pattern, stepregistry
):
    """
    Test registering Step function via given decorator
    """
    # given & when
    @given(pattern)
    def step_a(step):
        pass

    # then
    assert len(stepregistry.steps) == 1
    if not isinstance(pattern, re_pattern):  # doesn't work for re_pattern.
        assert stepregistry.steps[expected_pattern] == step_a


@pytest.mark.parametrize(
    "pattern, expected_pattern",
    [
        ("I do some stuff", "When I do some stuff"),
        (re.compile("I do some stuff"), re.compile("When I do some stuff")),
    ],
    ids=["Step with Step Pattern", "Step with Regex"],
)
def test_registering_step_function_via_when_decorator(
    pattern, expected_pattern, stepregistry
):
    """
    Test registering Step function via when decorator
    """
    # given & when
    @when(pattern)
    def step_a(step):
        pass

    # then
    assert len(stepregistry.steps) == 1
    if not isinstance(pattern, re_pattern):  # doesn't work for re_pattern.
        assert stepregistry.steps[expected_pattern] == step_a


@pytest.mark.parametrize(
    "pattern, expected_pattern",
    [
        ("I do some stuff", "Then I do some stuff"),
        (re.compile("I do some stuff"), re.compile("Then I do some stuff")),
    ],
    ids=["Step with Step Pattern", "Step with Regex"],
)
def test_registering_step_function_via_then_decorator(
    pattern, expected_pattern, stepregistry
):
    """
    Test registering Step function via then decorator
    """
    # given & when
    @then(pattern)
    def step_a(step):
        pass

    # then
    assert len(stepregistry.steps) == 1
    if not isinstance(pattern, re_pattern):  # doesn't work for re_pattern.
        assert stepregistry.steps[expected_pattern] == step_a


def test_registering_steps_from_object_via_steps_decorator(stepregistry):
    """
    Test registering Steps from object via steps decorator
    """
    # given & when
    @steps
    class MySteps(object):
        def some_step(self):
            """When I call some step"""

        def some_other_step(self):
            """
            I do some stuff

            This is not part of the step pattern
            """

    # then
    assert len(stepregistry.steps) == 2
    assert "When I call some step" in stepregistry.steps
    assert "I do some stuff" in stepregistry.steps


def test_getting_pattern_of_specific_func(stepregistry):
    """
    Test getting the pattern of a specific func
    """
    # given
    def step_a():
        pass

    def step_b():
        pass

    def step_c():
        pass

    stepregistry.register("step_pattern_a", step_a)
    stepregistry.register("step_pattern_b", step_b)

    # when
    pattern_a = stepregistry.get_pattern(step_a)
    pattern_b = stepregistry.get_pattern(step_b)
    pattern_c = stepregistry.get_pattern(step_c)

    # then
    assert pattern_a == "step_pattern_a"
    assert pattern_b == "step_pattern_b"
    assert pattern_c == "Unknown"
