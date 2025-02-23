"""
radish
~~~~~~

Behavior Driven Development tool for Python - the root from red to green

Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

from datetime import datetime, timezone

import pytest

from radish.exceptions import RadishError
from radish.extensions.junit_xml_writer import JUnitXMLWriter
from radish.feature import Feature
from radish.model import Tag
from radish.scenario import Scenario
from radish.terrain import world


def test_empty_feature_list():
    writer = JUnitXMLWriter()
    no_features = []

    with pytest.raises(RadishError):
        writer.generate_junit_xml(no_features, "marker-is-ignored")


def test_singel_feature_list(mocker):
    stub = mocker.patch("radish.extensions.junit_xml_writer.JUnitXMLWriter._write_xml_to_disk")

    first_feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    first_feature.starttime = datetime.now(timezone.utc)
    first_feature.endtime = datetime.now(timezone.utc)

    features = [first_feature]

    writer = JUnitXMLWriter()
    writer.generate_junit_xml(features, "marker-is-ignored")

    assert "I am a feature" in str(stub.call_args[0])


def test_normal_feature_list(mocker):
    world.config.junit_relaxed = False
    stub = mocker.patch("radish.extensions.junit_xml_writer.JUnitXMLWriter._write_xml_to_disk")

    tags = [Tag("author", "batman")]

    first_scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=tags,
        preconditions=None,
        background=None,
    )
    first_scenario.starttime = datetime.now(timezone.utc)
    first_scenario.endtime = datetime.now(timezone.utc)

    first_feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    first_feature.starttime = datetime.now(timezone.utc)
    first_feature.endtime = datetime.now(timezone.utc)
    first_feature.scenarios.append(first_scenario)

    features = [first_feature]

    writer = JUnitXMLWriter()
    writer.generate_junit_xml(features, "marker-is-ignored")

    assert "I am a Scenario" in str(stub.call_args[0])
    assert "properties" not in str(stub.call_args[0])


def test_relaxed_mode_adding_tags_to_junit(mocker):
    world.config.junit_relaxed = True
    stub = mocker.patch("radish.extensions.junit_xml_writer.JUnitXMLWriter._write_xml_to_disk")

    tags = [Tag("author", "batman")]

    first_scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=tags,
        preconditions=None,
        background=None,
    )
    first_scenario.starttime = datetime.now(timezone.utc)
    first_scenario.endtime = datetime.now(timezone.utc)

    first_feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    first_feature.starttime = datetime.now(timezone.utc)
    first_feature.endtime = datetime.now(timezone.utc)
    first_feature.scenarios.append(first_scenario)

    features = [first_feature]

    writer = JUnitXMLWriter()
    writer.generate_junit_xml(features, "marker-is-ignored")

    assert "author" in str(stub.call_args[0])
    assert "batman" in str(stub.call_args[0])
