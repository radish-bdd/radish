# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.extensionregistry import extension
import radish.exceptions as errors


def test_register_simple_extension_class(extensionregistry):
    """
    Test registering simple Extension class
    """
    # given
    class SimpleExtension(object):
        pass

    # when
    extensionregistry.register(SimpleExtension)

    # then
    assert len(extensionregistry.extensions) == 1
    assert extensionregistry.extensions[0] == SimpleExtension
    assert len(extensionregistry.loaded_extensions) == 0


def test_register_simple_extension_class_using_decorator(extensionregistry):
    """
    Test registering simple Extension class using the extension decorator
    """
    # given & when
    @extension
    class SimpleExtension(object):
        pass

    # then
    assert len(extensionregistry.extensions) == 1
    assert extensionregistry.extensions[0] == SimpleExtension
    assert len(extensionregistry.loaded_extensions) == 0


def test_loading_simple_extension(extensionregistry, mocker):
    """
    Test loading simple extension
    """
    # given
    @extension
    class SimpleExtension(object):
        LOAD_IF = staticmethod(lambda config: True)

    # when
    extensionregistry.load(mocker.MagicMock())

    # then
    assert len(extensionregistry.extensions) == 1
    assert extensionregistry.extensions[0] == SimpleExtension
    assert len(extensionregistry.loaded_extensions) == 1
    assert isinstance(extensionregistry.loaded_extensions[0], SimpleExtension)


# FIXME(TF): wrong behavior?!
def test_loading_invalid_extension(extensionregistry, mocker):
    """
    Test loading an invalid extension
    """
    # given
    @extension
    class SimpleExtension(object):
        pass

    # when
    extensionregistry.load(mocker.MagicMock())

    # then
    assert len(extensionregistry.extensions) == 1
    assert len(extensionregistry.loaded_extensions) == 0


def test_loading_extension_which_raises_exceptions_init(extensionregistry, mocker):
    """
    Test loading extension which raises exceptions in init
    """
    # given
    @extension
    class SimpleExtension(object):
        LOAD_IF = staticmethod(lambda config: True)

        def __init__(self):
            raise AssertionError("some error")

    # when
    with pytest.raises(AssertionError) as exc:
        extensionregistry.load(mocker.MagicMock())

    # then
    assert str(exc.value) == "some error"


def test_loading_simple_extension_if_wanted(extensionregistry, mocker):
    """
    Test loading extension if wanted by config
    """
    # given
    @extension
    class WantedExtension(object):
        LOAD_IF = staticmethod(lambda config: True)

    @extension
    class UnwantedExtension(object):
        LOAD_IF = staticmethod(lambda config: False)

    # when
    extensionregistry.load(mocker.MagicMock())

    # then
    assert len(extensionregistry.extensions) == 2
    assert len(extensionregistry.loaded_extensions) == 1
    assert isinstance(extensionregistry.loaded_extensions[0], WantedExtension)


def test_extension_loading_order(extensionregistry, mocker):
    """
    Test the loading order of extensions
    """
    # given
    @extension
    class SecondExtension(object):
        LOAD_IF = staticmethod(lambda config: True)
        # default prio = 1000

    @extension
    class FirstExtension(object):
        LOAD_IF = staticmethod(lambda config: True)
        LOAD_PRIORITY = 1

    @extension
    class ThirdExtension(object):
        LOAD_IF = staticmethod(lambda config: True)
        LOAD_PRIORITY = 10000

    # when
    extensionregistry.load(mocker.MagicMock())

    # then
    assert len(extensionregistry.loaded_extensions) == 3
    assert isinstance(extensionregistry.loaded_extensions[0], FirstExtension)
    assert isinstance(extensionregistry.loaded_extensions[1], SecondExtension)
    assert isinstance(extensionregistry.loaded_extensions[2], ThirdExtension)


def test_getting_extension_options(extensionregistry, mocker):
    """
    Test getting command line options from extensions
    """
    # given
    @extension
    class FooExtension(object):
        OPTIONS = [("--foo", "enable foo power")]

    @extension
    class BarExtension(object):
        OPTIONS = [
            ("--bar", "enable bar power"),
            ("--bar-pow", "enable magnitude of bar power"),
        ]

    @extension
    class BlaExtension(object):
        pass

    # when
    options = extensionregistry.get_options()
    option_description = extensionregistry.get_option_description()

    # then
    assert (
        options
        == """[--foo]
           [--bar]
           [--bar-pow]"""
    )

    assert (
        option_description
        == """--foo                                       enable foo power
    --bar                                       enable bar power
    --bar-pow                                   enable magnitude of bar power"""
    )
