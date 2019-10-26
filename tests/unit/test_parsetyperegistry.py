"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.parsetyperegistry import ParseTypeRegistry
from radish.errors import RadishError


def test_parsetyperegistry_should_initialize_without_any_registered_types():
    """The ParseTypeRegistry should be initialized wihtout any pre-registered Custom Parse Types"""
    # when
    registry = ParseTypeRegistry()

    # then
    assert registry.types == {}


def test_parsetyperegistry_should_register_funcs_as_custom_parse_types():
    """The ParseTypeRegistry should register a function with a given name as a Custom Parse Type"""
    # given
    registry = ParseTypeRegistry()
    custom_parse_type_func = lambda x: x  # noqa

    # when
    registry.register("name", custom_parse_type_func, "pattern")

    # then
    assert registry.types == {"name": custom_parse_type_func}


def test_parsetyperegistry_should_only_allow_unique_custom_parse_type_names():
    """
    The ParseTypeRegistry should only allow to register new
    Custom Parse Types with unique names
    """
    # given
    registry = ParseTypeRegistry()
    custom_parse_type_func = lambda x: x  # noqa
    registry.register("name", custom_parse_type_func, "pattern")

    # then
    with pytest.raises(RadishError):
        # when
        registry.register("name", custom_parse_type_func, "pattern")


def test_parsetyperegistry_should_assign_pattern_to_func_during_register():
    """
    The ParseTypeRegistry should assign the Custom Type Parse pattern
    to the function which is registered as type handler.
    """
    # given
    registry = ParseTypeRegistry()
    custom_parse_type_func = lambda x: x  # noqa

    # when
    registry.register("name", custom_parse_type_func, "pattern")

    # then
    assert custom_parse_type_func.pattern == "pattern"


def test_parsetyperegistry_should_create_custom_type_decorator_into_context():
    """
    The ParseTypeRegistry should only allow to register new
    Custom Parse Types with unique names
    """
    # given
    registry = ParseTypeRegistry()
    context = {}

    # when
    created_decorator_name = registry.create_decorator(context)

    # then
    assert created_decorator_name == "custom_type"
    assert "custom_type" in context
    assert callable(context["custom_type"])


def test_parsetyperegistry_should_register_custom_parse_type_via_decorator():
    """
    The ParseTypeRegistry should only to register a Custom Parse Type
    with the created @custom_type decorator.
    """
    # given
    registry = ParseTypeRegistry()
    context = {}
    registry.create_decorator(context)

    decorator = context["custom_type"]

    # when
    @decorator("name", "pattern")
    def my_custom_type(text):
        ...

    # then
    assert registry.types == {"name": my_custom_type}
