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


def test_make_unique_obj_list():
    """
    Test filter list by propertyName
    """
    object_list = [ type('SomeObjectClass', (object,), {'propertyName' : '1'}),
                    type('SomeObjectClass', (object,), {'propertyName' : '2'}),
                    type('SomeObjectClass', (object,), {'propertyName' : '1'}),
    ]

    value_list = utils.make_unique_obj_list(object_list, lambda x: x.propertyName)
    value_list = list(map(lambda x: x.propertyName, value_list))
    value_list.sort()

    assert value_list == ['1', '2']
