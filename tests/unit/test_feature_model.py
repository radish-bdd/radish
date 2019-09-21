"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.models import Feature, State
from radish.models import ConstantTag, Tag


@pytest.mark.parametrize(
    "given_rule_states, expected_state",
    [
        ([State.PASSED, State.PASSED, State.PASSED], State.PASSED),
        ([State.PASSED, State.UNTESTED, State.PASSED], State.UNTESTED),
        ([State.PASSED, State.SKIPPED, State.UNTESTED], State.SKIPPED),
        ([State.PASSED, State.PENDING, State.SKIPPED], State.PENDING),
        ([State.PASSED, State.PENDING, State.FAILED], State.FAILED),
        ([State.PASSED, State.RUNNING, State.FAILED], State.RUNNING),
    ],
    ids=[
        "[State.PASSED, State.PASSED, State.PASSED] -> State.PASSED",
        "[State.PASSED, State.UNTESTED, State.PASSED] -> State.UNTESTED",
        "[State.PASSED, State.SKIPPED, State.UNTESTED] -> State.SKIPPED",
        "[State.PASSED, State.PENDING, State.SKIPPED] -> State.PENDING",
        "[State.PASSED, State.PENDING, State.FAILED] -> State.FAILED",
        "[State.PASSED, State.RUNNING, State.FAILED] -> State.RUNNING",
    ],
)
def test_feature_should_return_correct_state_according_to_its_rule_states(
    given_rule_states, expected_state, mocker
):
    """A Feature should return the correct State according to its rule States"""
    # given
    feature = Feature(
        1,
        "Feature",
        "My Feature",
        None,
        [],
        None,
        None,
        None,
        [mocker.MagicMock(state=s) for s in given_rule_states],
        None,
    )

    # when
    actual_state = feature.state

    # then
    assert actual_state == expected_state


@pytest.mark.parametrize(
    "rules_need_to_run, expected_has_to_run",
    [
        ([False, False, False], False),
        ([False, True, False], True),
        ([False, True, True], True),
    ],
    ids=["no Rule needs to run", "a Rule needs to run", "multiple Rules need to run"],
)
def test_feature_should_run_if_one_of_its_rule_has_to_run(
    rules_need_to_run, expected_has_to_run, mocker
):
    """A Feature should run if one of its Rules has to run"""
    rules = []
    for has_to_run in rules_need_to_run:
        rule_mock = mocker.MagicMock()
        rule_mock.has_to_run.return_value = has_to_run
        rules.append(rule_mock)

    # given
    feature = Feature(
        1, "Feature", "My Feature", None, [], None, None, None, rules, None
    )

    # when
    actual_has_to_run = feature.has_to_run(None, None)

    # then
    assert actual_has_to_run == expected_has_to_run


def test_feature_should_return_all_constants():
    """A Feature should return all Constants from the Tags"""
    # given
    tags = [
        Tag("x", None, None),
        ConstantTag("k1", "v1", None, None),
        Tag("y", None, None),
        ConstantTag("k2", "v2", None, None),
    ]
    feature = Feature(
        1, "Feature", "My Feature", None, tags, None, None, None, None, None
    )

    # when
    actual_constants = feature.constants

    # then
    assert actual_constants == {"k1": "v1", "k2": "v2"}
