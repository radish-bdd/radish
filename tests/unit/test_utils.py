# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

import radish.utils as utils


@pytest.mark.parametrize('basedirs, expected_basedirs', [
    (['foo', 'bar'], ['foo', 'bar']),
    (['foo:bar', 'foobar'], ['foo', 'bar', 'foobar']),
    (['foo:bar', 'foobar', 'one:two:three'],
        ['foo', 'bar', 'foobar', 'one', 'two', 'three']),
    (['foo:', ':bar'], ['foo', 'bar'])
])
def test_flattened_basedirs(basedirs, expected_basedirs):
    """
    Test flatten basedirs
    """
    # given & when
    actual_basedirs = utils.flattened_basedirs(basedirs)

    # then
    assert actual_basedirs == expected_basedirs
