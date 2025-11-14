"""
radish
~~~~~~

Behavior Driven Development tool for Python - the root from red to green

Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

from datetime import datetime, timezone
from threading import Lock, Thread

import pytest
from freezegun import freeze_time

from radish import utils


@pytest.mark.parametrize(
    "basedirs, expected_basedirs, os_name",
    [
        (["foo", "bar"], ["foo", "bar"], "posix"),
        (["foo:bar", "foobar"], ["foo", "bar", "foobar"], "posix"),
        (["foo:bar", "foobar", "one:two:three"], ["foo", "bar", "foobar", "one", "two", "three"], "posix"),
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
    utc_dt = datetime.now(timezone.utc)
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
    value_list = [x.propertyName for x in value_list]
    value_list.sort()

    assert value_list == ["1", "2"]


def test_singleton_behavior():
    """Test that Singleton metaclass enforces singleton behavior"""

    class MySingletonClass(metaclass=utils.Singleton):
        def __init__(self):
            self.value = 42

    instance1 = MySingletonClass()
    instance1.value = 100
    instance2 = MySingletonClass()

    assert instance1 is instance2
    assert instance1.value == instance2.value


def test_singleton_thread_safety():
    """Test that Singleton metaclass is thread-safe"""

    class MyThreadSafeSingleton(metaclass=utils.Singleton):
        def __init__(self):
            self.value = 0

    instances = []
    lock = Lock()

    def create_instance():
        instance = MyThreadSafeSingleton()
        with lock:  # Ensure thread-safe appending
            instances.append(instance)

    threads = [Thread(target=create_instance) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    first_instance = instances[0]
    for instance in instances:
        assert instance is first_instance
