"""
radish
~~~~~~

Behavior Driven Development tool for Python - the root from red to green

Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import re
from datetime import datetime, timezone

import pytest

from radish.exceptions import RadishError
from radish.extensions.junit_xml_writer import JUnitXMLWriter
from radish.feature import Feature
from radish.model import Tag
from radish.scenario import Scenario
from radish.stepmodel import Step
from radish.terrain import world


def test_empty_feature_list():
    writer = JUnitXMLWriter()
    no_features = []

    with pytest.raises(RadishError):
        writer.generate_junit_xml(no_features, "marker-is-ignored")


def test_single_feature_list(mocker):
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


def test_early_exit_feature_list(mocker):
    stub = mocker.patch("radish.extensions.junit_xml_writer.JUnitXMLWriter._write_xml_to_disk")

    first_feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    first_feature.starttime = datetime.now(timezone.utc)
    first_feature.endtime = datetime.now(timezone.utc)
    second_feature = Feature(2, "Feature", "Did not run", "foo.feature", 1, tags=None)
    # second_feature.state = Step.State.UNTESTED
    scenario = Scenario(
        1, "Scenario", "Did not run", "foo.feature", 1, parent=None, tags=None, preconditions=None, background=None
    )
    scenario.steps = [Step(1, "Foo", "foo.feature", 2, None, False)]
    second_feature.scenarios = [scenario]
    assert second_feature.state not in [Step.State.PASSED, Step.State.FAILED]

    features = [first_feature, second_feature]

    writer = JUnitXMLWriter()
    writer.generate_junit_xml(features, "marker-is-ignored")

    result = str(stub.call_args[0])
    feature_regex = re.compile(r"<testsuite[^>]*name=\"([^\"]+)\"([^>]*)>")
    matches = feature_regex.findall(result)
    assert len(matches) == 2
    f1_match = next(m for m in matches if m[0] == "I am a feature")
    f2_match = next(m for m in matches if m[0] == "Did not run")
    assert 'tests="0"' in f1_match[1]  # f1 contains no scenarios
    assert 'skipped="1"' in f2_match[1]  # f2 contains one untested scenario (it was skipped)
    assert "<skipped" in result  # there is a skipped testcase element
