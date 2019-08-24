"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.hookregistry import HookRegistry, HookImpl


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
    assert callable(before.each_scenario)
    assert callable(before.each_step)
    assert callable(after.all)
    assert callable(after.each_feature)
    assert callable(after.each_scenario)
    assert callable(after.each_step)
