# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

from datetime import datetime

import pytest
from freezegun import freeze_time

import radish.utils as utils


@pytest.mark.parametrize(
    "basedirs, expected_basedirs, os_name",
    [
        (["foo", "bar"], ["foo", "bar"], "posix"),
        (["foo:bar", "foobar"], ["foo", "bar", "foobar"], "posix"),
        (
            ["foo:bar", "foobar", "one:two:three"],
            ["foo", "bar", "foobar", "one", "two", "three"],
            "posix"
        ),
        (["foo:", ":bar"], ["foo", "bar"], "posix"),
        (["C:\\windows\\radish"], ["C:\\windows\\radish"], "nt"),
        (["C:\\windows;radish"], ["C:\\windows", "radish"], "nt"),
    ],
)
def test_flattened_basedirs(mocker, basedirs, expected_basedirs, os_name):
    """
    Test flatten basedirs
    """
    # given & when
    mocker.patch("os.name", os_name)
    actual_basedirs = utils.flattened_basedirs(basedirs)

    # then
    assert actual_basedirs == expected_basedirs


@freeze_time("2015-10-21 04:29:00", tz_offset=+1)
def test_date_time_formatter():
    """
    Test datetime to string format
    """
    # given
    utc_dt = datetime.utcnow()
    expected_datetime_string = "2015-10-21T05:29:00"
    actual_datetime_string = utils.format_utc_to_local_tz(utc_dt)

    # then
    assert actual_datetime_string == expected_datetime_string


def test_make_unique_obj_list():
    """
    Test filter list by propertyName
    """
    object_list = [
        type("SomeObjectClass", (object,), {"propertyName": "1"}),
        type("SomeObjectClass", (object,), {"propertyName": "2"}),
        type("SomeObjectClass", (object,), {"propertyName": "1"}),
    ]

    value_list = utils.make_unique_obj_list(object_list, lambda x: x.propertyName)
    value_list = list(map(lambda x: x.propertyName, value_list))
    value_list.sort()

    assert value_list == ["1", "2"]
