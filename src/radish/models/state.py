"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from enum import IntEnum


class State(IntEnum):
    """Represent the State of a Model

    A Model can be one of:

    * :class:`Step`
    * :class:`Scenario`
    * :class:`Feature`
    """

    PASSED = 0  #: State which is set for a :class:`Step` if it ran successfully
    UNTESTED = 1  #: Default State for all :class:`Step`
    SKIPPED = 2  #: State which is set for a :class:`Step` when it's skipped using :func:`Step.skip`
    PENDING = 3  #: State which is set for a :class:`Step` when it's marked pending using :func:`Step.pending`  # noqa
    FAILED = 4  #: State which is set for a :class:`Step` when it failed to run it
    RUNNING = 5  #: State which is set while a :class:`Step` is running

    @staticmethod
    def report_state(states):
        """Report the single most appropriate State out of a list of States"""
        try:
            return sorted(states, reverse=True)[0]
        except IndexError:
            # states generator did not yield any States
            return State.UNTESTED
