"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest
from tagexpressions import parse

from radish.models import Feature, Tag


@pytest.mark.parametrize("tagexpression, expected_has_to_run", [
    (None, True),
], ids=[
    "no tagexpression => RUN"
])
def test_feature_should_correctly_evaluate_if_it_has_to_be_run(
    tagexpression, expected_has_to_run
):
    """Test that a Feature should correctly evaluate if it has to be run or not"""
    # given
    feature = Feature(
        1, "My Feature", "",
        [Tag("tag-a", None, None), Tag("tag-b", None, None)],
        None, None,
        None, []
    )

    # when
    has_to_run = feature.has_to_run(tagexpression)

    # then
    assert has_to_run == expected_has_to_run
