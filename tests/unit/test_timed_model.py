"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from datetime import timedelta

from freezegun import freeze_time

from radish.models.timed import Timed


def test_timed_model_should_be_created_without_a_start_and_end_time():
    """A Timed model should be created without a start- and end time"""
    # when
    model = Timed()

    # then
    assert model.starttime is None
    assert model.endtime is None


@freeze_time("1994-02-21")
def test_timed_model_should_record_current_time_when_recording_started():
    """A Timed model should record the current time when the recording is started"""
    # given
    model = Timed()

    # when
    model.record_starttime()

    # then
    model.starttime == 761788800


@freeze_time("1994-02-21")
def test_timed_model_should_record_current_time_when_recording_ended():
    """A Timed model should record the current time when the recording is ended"""
    # given
    model = Timed()

    # when
    model.record_endtime()

    # then
    model.starttime == 761788800


def test_timed_model_zero_duration_when_recording_not_started():
    """A Timed model should calculated a duration of ZERO when the recording was not started"""
    # given
    model = Timed()

    # when
    duration = model.duration()

    # then
    assert duration == timedelta(0)


@freeze_time("1994-02-22")
def test_timed_model_should_give_the_current_duration_when_only_starttime_recorded():
    """
    A Timed model should calulated the duration until the
    current time when only the starttime is recorded
    """
    # given
    model = Timed()
    model.starttime = 761788800  # 1994-02-21

    # when
    duration = model.duration()

    # then
    assert duration == timedelta(days=1)


@freeze_time("1994-02-22")
def test_timed_model_should_calculate_the_duration_between_recorded_start_and_end_time():
    """
    A Timed model should calulated the duration between
    a recorded start- and end time.
    """
    # given
    model = Timed()
    model.starttime = 761788800  # 1994-02-21
    model.endtime = model.starttime + 60  # plus a minute

    # when
    duration = model.duration()

    # then
    assert duration == timedelta(minutes=1)
