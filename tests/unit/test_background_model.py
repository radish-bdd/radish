"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.models.state import State
from radish.models.background import Background


@pytest.mark.parametrize(
    "given_step_states, expected_state",
    [
        ([State.PASSED, State.PASSED, State.PASSED], State.PASSED),
        ([State.PASSED, State.UNTESTED, State.PASSED], State.UNTESTED),
        ([State.PASSED, State.SKIPPED, State.UNTESTED], State.SKIPPED),
        ([State.PASSED, State.PENDING, State.SKIPPED], State.PENDING),
        ([State.PASSED, State.FAILED, State.PENDING], State.FAILED),
        ([State.PASSED, State.RUNNING, State.FAILED], State.RUNNING),
    ],
    ids=[
        "[State.PASSED, State.PASSED, State.PASSED] -> State.PASSED",
        "[State.PASSED, State.UNTESTED, State.PASSED] -> State.UNTESTED",
        "[State.PASSED, State.SKIPPED, State.UNTESTED] -> State.SKIPPED",
        "[State.PASSED, State.PENDING, State.SKIPPED] -> State.PENDING",
        "[State.PASSED, State.FAILED, State.PENDING] -> State.FAILED",
        "[State.PASSED, State.RUNNING, State.FAILED] -> State.RUNNING",
    ],
)
def test_background_should_correct_state(given_step_states, expected_state, mocker):
    """A Background should return the worst State of its Steps State as its own State"""
    # given
    background = Background(
        "Background",
        "Background",
        None,
        None,
        [mocker.MagicMock(state=s) for s in given_step_states],
    )

    # when
    actual_state = background.state

    # then
    assert actual_state == expected_state
