"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from enum import IntEnum


class State(IntEnum):
    """Represents the State of other models"""

    PASSED = 0
    UNTESTED = 1
    RUNNING = 2
    SKIPPED = 3
    PENDING = 4
    FAILED = 5

    @staticmethod
    def report_state(states):
        """Report the single most appropriate State out of a list of States"""
        return sorted(states, reverse=True)[0]
