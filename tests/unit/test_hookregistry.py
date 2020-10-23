"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from unittest import mock

import pytest

from radish.hookregistry import GeneratorHookImpl, HookImpl, HookRegistry
from radish.models import Tag


@pytest.mark.parametrize(
    "hook_1, hook_2, expect_equal",
    [
        (
            HookImpl("what", "when", None, [], 1),
            HookImpl("what", "when", None, [], 1),
            True,
        ),
        (
            HookImpl("what", "when", None, [], 1),
            HookImpl("", "when", None, [], 1),
            False,
        ),
        (
            HookImpl("what", "when", None, [], 1),
            HookImpl("what", "", None, [], 1),
            False,
        ),
        (
            HookImpl("what", "when", None, [], 1),
            HookImpl("what", "when", lambda x: x, [], 1),
            False,
        ),
        (
            HookImpl("what", "when", None, [], 1),
            HookImpl("what", "when", None, [1], 1),
            False,
        ),
        (
            HookImpl("what", "when", None, [], 1),
            HookImpl("what", "when", None, [], 2),
            False,
        ),
    ],
)
def test_hookimpls_can_be_compared_by_equality(hook_1, hook_2, expect_equal):
    """The ``HookImpl``s can be compared for their equality"""
    # when
    are_equal = hook_1 == hook_2

    # then
    assert are_equal == expect_equal


def test_hookimpls_can_be_called():
    # given
    def func(x, y, foo=None):
        return x, y, foo

    hook = HookImpl("what", "when", func, [], 1)

    # when
    x, y, foo = hook(1, 2, foo=3)

    # then
    assert x == 1
    assert y == 2
    assert foo == 3


def test_generatorhookimpls_can_be_called_twice_to_exhaust_generator():
    # given
    def func(x, y, foo=None):
        x += 1
        y += 1
        foo += 1
        yield x, y, foo
        x += 1
        y += 1
        foo += 1
        yield x, y, foo

    hook = GeneratorHookImpl(func)

    # when
    first_x, first_y, first_foo = hook(1, 2, foo=3)
    second_x, second_y, second_foo = hook(1, 2, foo=3)

    # then
    assert first_x == 2
    assert first_y == 3
    assert first_foo == 4
    assert second_x == 3
    assert second_y == 4
    assert second_foo == 5


def test_hookimpls_can_be_sorted_by_the_order():
    """The ``HookImpl``s can be sorted by it's order"""
    # given
    hooks = [
        HookImpl("what", "when", None, [], 1),
        HookImpl("what", "when", None, [], 10),
        HookImpl("what", "when", None, [], 5),
        HookImpl("what", "when", None, [], 2),
        HookImpl("what", "when", None, [], 30),
        HookImpl("what", "when", None, [], 8),
        HookImpl("what", "when", None, [], 7),
    ]

    # when
    sorted_hooks = sorted(hooks)

    # then
    assert sorted_hooks == [
        HookImpl("what", "when", None, [], 1),
        HookImpl("what", "when", None, [], 2),
        HookImpl("what", "when", None, [], 5),
        HookImpl("what", "when", None, [], 7),
        HookImpl("what", "when", None, [], 8),
        HookImpl("what", "when", None, [], 10),
        HookImpl("what", "when", None, [], 30),
    ]


def test_hookregistry_module_should_have_global_registry_instance():
    """The radish.hookregistry module should contain a global HookRegistry instance"""
    # given & when
    from radish.hookregistry import registry

    # then
    assert isinstance(registry, HookRegistry)


def test_hookregistry_module_should_have_global_hook_decorators():
    """The radish.hookregistry module should contain functions for the Hook decorators"""
    # given & when
    from radish.hookregistry import before, after

    # then
    assert callable(before.all)
    assert callable(before.each_feature)
    assert callable(before.each_rule)
    assert callable(before.each_scenario)
    assert callable(before.each_step)
    assert callable(after.all)
    assert callable(after.each_feature)
    assert callable(after.each_rule)
    assert callable(after.each_scenario)
    assert callable(after.each_step)


def test_hookregistry_module_should_have_global_generator_hook_decorators():
    # given & when
    from radish.hookregistry import (
        for_all,
        each_feature,
        each_rule,
        each_scenario,
        each_step,
    )

    # then
    assert callable(for_all)
    assert callable(each_feature)
    assert callable(each_rule)
    assert callable(each_scenario)
    assert callable(each_step)


def test_hookregistry_call_hook_func_if_match(mocker):
    # given
    registry = HookRegistry()

    to_be_called_hook_func = mocker.MagicMock(name="before_each_scenario_func")
    not_to_be_called_hook = mocker.MagicMock(name="after_each_scenario_func")

    registry.register(
        what="each_scenario",
        when="before",
        func=to_be_called_hook_func,
        on_tags=[],
        order=1,
    )
    registry.register(
        what="each_scenario",
        when="after",
        func=not_to_be_called_hook,
        on_tags=[],
        order=1,
    )

    # when
    registry.call(
        "each_scenario", "before", False, mocker.MagicMock(name="TaggedModel")
    )

    # then
    to_be_called_hook_func.assert_has_calls([mock.call(mock.ANY)])
    not_to_be_called_hook.assert_has_calls([])


def test_hookregistry_call_hook_func_if_tag_matched(mocker):
    # given
    registry = HookRegistry()

    to_be_called_hook_func = mocker.MagicMock(name="before_each_scenario_func_tagged")
    not_to_be_called_hook = mocker.MagicMock(name="before_each_scenario_func")

    registry.register(
        what="each_scenario",
        when="before",
        func=to_be_called_hook_func,
        on_tags=["some-tag"],
        order=1,
    )
    registry.register(
        what="each_scenario",
        when="before",
        func=not_to_be_called_hook,
        on_tags=["another-tag"],
        order=1,
    )

    tagged_model = mocker.MagicMock(name="TaggedModel")
    tagged_model.get_all_tags.return_value = [Tag(name="some-tag", path="", line=0)]

    # when
    registry.call("each_scenario", "before", False, tagged_model)

    # then
    to_be_called_hook_func.assert_has_calls([mock.call(mock.ANY)])
    not_to_be_called_hook.assert_has_calls([])
