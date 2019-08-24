"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.config import Config
from radish.errors import RadishError


def test_config_adds_items_as_attributes():
    """The Config objects adds its Config Items as object attributes"""
    # when
    config = Config({"foo": "bar", "bla": "meh"})

    # then
    assert config.foo == "bar"
    assert config.bla == "meh"


def test_config_parses_tag_expressions():
    """The Config object parses Tag Expressions"""
    # when
    config = Config({"tags": "foo and bar"})

    # then
    assert config.tag_expression is not None


def test_config_raise_error_for_invalid_tag_expressions():
    """The Config object should raise an Error for an invalid Tag Expression"""
    # then
    with pytest.raises(RadishError):
        # when
        Config({"tags": "foo and"})
