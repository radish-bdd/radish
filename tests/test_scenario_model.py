"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest
from tagexpressions import parse

from radish.models import Scenario, Tag


@pytest.mark.parametrize(
    "tagexpression, scenario_ids, expected_has_to_run",
    [
        (None, [], True),
        (parse("tag-a"), [], True),
        (parse("tag-c"), [], True),
        (parse("tag-X"), [], False),
        (None, [1], True),
        (None, [2], False),
        (parse("tag-a"), [2], False),
        (parse("tag-X"), [1], False),
        (parse("tag-a"), [1], True),
    ],
    ids=[
        "no tagexpression, no scenario_ids => RUN",
        "tagexpression match in Scenario Tags, no scenario_ids => RUN",
        "tagexpression match in Feature Tags, no scenario_ids => RUN",
        "tagexpression no match, no scenario_ids => NO RUN",
        "no tagexpression, scenario_ids match => RUN",
        "no tagexpression, scenario_ids no match => NO RUN",
        "tagexpression match, scenario_ids no match => NO RUN",
        "tagexpression no match, scenario_ids match => NO RUN",
        "tag expression match, scenario_ids match => RUN",
    ],
)
def test_scenario_should_correctly_evaluate_if_it_has_to_be_run(
    mocker, tagexpression, scenario_ids, expected_has_to_run
):
    """Test that a Scenario should correctly evaluate if it has to be run or not"""
    # given
    feature_mock = mocker.MagicMock(tags=[Tag("tag-c", None, None)])
    scenario = Scenario(
        1,
        "My Scenario",
        [Tag("tag-a", None, None), Tag("tag-b", None, None)],
        None,
        None,
        [],
    )
    scenario.set_feature(feature_mock)

    # when
    has_to_run = scenario.has_to_run(tagexpression, scenario_ids)

    # then
    assert has_to_run == expected_has_to_run
