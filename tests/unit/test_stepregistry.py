"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.stepregistry import StepImpl, StepRegistry


@pytest.mark.parametrize(
    "step_impl_1, step_impl_2, expected_equal",
    [
        (StepImpl("Given", "pattern", None), StepImpl("Given", "pattern", None), True),
        (StepImpl("Given", "pattern", None), StepImpl("", "pattern", None), False),
        (StepImpl("Given", "pattern", None), StepImpl("Given", "", None), False),
        (
            StepImpl("Given", "pattern", None),
            StepImpl("Given", "pattern", lambda x: x),
            False,
        ),
        (StepImpl("Given", "pattern", None), None, False),
    ],
    ids=[
        "are equal",
        "keyword is not equal",
        "pattern is not equal",
        "func is not equal",
        "right hand side object is no StepImpl object",
    ],
)
def test_step_impl_should_implement_the_equals_protocol(
    step_impl_1, step_impl_2, expected_equal
):
    """Test that StepImpls correctly implement the equals protocol"""
    # when
    are_equal = step_impl_1 == step_impl_2
    hash_equal = hash(step_impl_1) == hash(step_impl_2)

    # then
    assert are_equal == expected_equal
    assert hash_equal == expected_equal


def test_stepregistry_is_initialized_with_no_step_impls():
    """The StepRegistry should be initialized with no registered Step Implementations"""
    # given & when
    registry = StepRegistry()

    # then
    assert registry.step_implementations() == {}


def test_stepregistry_should_allow_to_register_step_impls():
    """The StepRegistry should allow to register a Step Implementation"""
    # given
    registry = StepRegistry()

    # when
    registry.register("Given", "pattern", None)

    # then
    assert registry.step_implementations("Given") == [
        StepImpl("Given", "pattern", None)
    ]


def test_stepregistry_should_gracefully_accept_double_registration():
    """
    The StepRegistry should gracefully accept a duplicate registration of a Step Implementation
    """
    # given
    registry = StepRegistry()
    registry.register("Given", "pattern", None)

    # when
    registry.register("Given", "pattern", None)

    # then
    assert registry.step_implementations("Given") == [
        StepImpl("Given", "pattern", None)
    ]


def test_stepregistry_should_create_one_step_decorator_per_keyword():
    """The StepRegistry should create one Step decorator for each keyword"""
    # given
    registry = StepRegistry()
    context = {}

    # when
    registry.create_step_decorators(context)

    # then
    assert len(context) == 4
    assert "given" in context
    assert "when" in context
    assert "then" in context
    assert "step" in context


@pytest.mark.parametrize("keyword", ["Given", "When", "Then"])
def test_stepregistry_step_decorator_should_register_func_with_proper_keyword(keyword):
    """The StepRegistry should create one Step decorator for each keyword"""
    # given
    registry = StepRegistry()
    context = {}
    registry.create_step_decorators(context)

    # when
    def test_step():
        ...

    test_step = context[keyword.lower()]("pattern")(test_step)

    # then
    assert registry.step_implementations(keyword) == [
        StepImpl(keyword, "pattern", test_step)
    ]


def test_stepregitry_register_func_with_multiple_decorators():
    """The StepRegistry should allow a function to be registered with multiple Step decorators"""
    # given
    registry = StepRegistry()
    context = {}
    registry.create_step_decorators(context)

    # when
    def test_step():
        ...

    test_step = context["given"]("pattern")(test_step)
    test_step = context["when"]("pattern")(test_step)

    # then
    assert registry.step_implementations("Given") == [
        StepImpl("Given", "pattern", test_step)
    ]
    assert registry.step_implementations("When") == [
        StepImpl("When", "pattern", test_step)
    ]


def test_stepregitry_step_decorators_for_all_keywords():
    """The StepRegistry should return the Step Implementations registered
    with the ``step`` decorator for all keywords.
    """
    # given
    registry = StepRegistry()
    context = {}
    registry.create_step_decorators(context)

    # when
    def test_step():
        ...

    test_step = context["step"]("pattern")(test_step)

    # then
    assert registry.step_implementations("Given") == [
        StepImpl("Step", "pattern", test_step)
    ]


def test_stepregistry_module_should_have_global_registry_instance():
    """The radish.stepregistry module should contain a global StepRegistry instance"""
    # given & when
    from radish.stepregistry import registry

    # then
    assert isinstance(registry, StepRegistry)


def test_stepregistry_module_should_have_global_step_decorators():
    """The radish.stepregistry module should contain functions for the Step decorators"""
    # given & when
    from radish.stepregistry import given, when, then, step

    # then
    assert callable(given)
    assert callable(when)
    assert callable(then)
    assert callable(step)


def test_stepregistry_module_level_given_decorator_register_at_global_registry_instance():
    """
    The global module-level given-Step decorators should register
    a Step at the global registry instance
    """
    # given
    from radish.stepregistry import registry, given

    # when
    @given("pattern")
    def given_step():
        ...

    # then
    assert StepImpl("Given", "pattern", given_step) in registry.step_implementations(
        "Given"
    )


def test_stepregistry_module_level_when_decorator_register_at_global_registry_instance():
    """
    The global module-level when-Step decorators should register
    a Step at the global registry instance
    """
    # given
    from radish.stepregistry import registry, when

    # when
    @when("pattern")
    def when_step():
        ...

    # then
    assert StepImpl("When", "pattern", when_step) in registry.step_implementations(
        "When"
    )


def test_stepregistry_module_level_then_decorator_register_at_global_registry_instance():
    """
    The global module-level then-Step decorators should register
    a Step at the global registry instance
    """
    # given
    from radish.stepregistry import registry, then

    # when
    @then("pattern")
    def then_step():
        ...

    # then
    assert StepImpl("Then", "pattern", then_step) in registry.step_implementations(
        "Then"
    )


def test_stepregistry_module_level_step_decorator_register_at_global_registry_instance():
    """
    The global module-level step-Step decorators should register
    a Step at the global registry instance
    """
    # given
    from radish.stepregistry import registry, step

    # when
    @step("pattern")
    def step_step():
        ...

    # then
    assert StepImpl("Step", "pattern", step_step) in registry.step_implementations(
        "Step"
    )
