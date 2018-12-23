# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import time

import pytest

from radish.model import Model, Tag
from radish.exceptions import RadishError


def test_creating_simple_model():
    """
    Test creating a simple Model
    """
    # given & when
    model = Model(1, "Model", "I am a Model", "foo.feature", 1, parent=None, tags=None)

    # then
    assert model.id == 1
    assert model.keyword == "Model"
    assert model.sentence == "I am a Model"
    assert model.path == "foo.feature"
    assert model.line == 1
    assert model.parent is None
    assert model.tags == []


def test_creating_a_tag():
    """
    Test creating a Tag
    """
    # given & when
    tag = Tag("foo", arg="bar")

    # then
    assert tag.name == "foo"
    assert tag.arg == "bar"


def test_getting_tags_from_model():
    """
    Test getting all Tags from a Model
    """
    # given & when
    parent_model = Model(
        1,
        "Model",
        "I am a Model",
        "foo.feature",
        1,
        parent=None,
        tags=[Tag("some_tag")],
    )
    model = Model(
        1,
        "Model",
        "I am a Model",
        "foo.feature",
        1,
        parent=parent_model,
        tags=[Tag("foo"), Tag("bar")],
    )

    # when
    tags = model.all_tags

    # then
    assert len(tags) == 3
    assert tags[0].name == "some_tag"
    assert tags[1].name == "foo"
    assert tags[2].name == "bar"


def test_getting_model_duration():
    """
    Test getting duration of a Model
    """
    # given & when
    model = Model(1, "Model", "I am a Model", "foo.feature", 1, parent=None, tags=None)
    model.starttime = time.time()
    model.endtime = model.starttime + 10

    # when
    duration = model.duration

    # then
    assert duration == 10


def test_getting_model_duration_with_missing_time():
    """
    Test getting duration of a Model with missing start- or endtime
    """
    # given & when
    model = Model(1, "Model", "I am a Model", "foo.feature", 1, parent=None, tags=None)

    # when - missing starttime
    model.starttime = None
    with pytest.raises(RadishError) as exc:
        model.duration
    # then
    assert (
        str(exc.value)
        == "Cannot get duration of Model 'I am a Model' because either starttime or endtime is not set"
    )

    # when - missing starttime
    model.starttime = time.time()
    with pytest.raises(RadishError) as exc:
        model.duration
    # then
    assert (
        str(exc.value)
        == "Cannot get duration of Model 'I am a Model' because either starttime or endtime is not set"
    )
