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
    SKIPPED = 2
    PENDING = 3
    FAILED = 4
    RUNNING = 5

    @staticmethod
    def report_state(states):
        """Report the single most appropriate State out of a list of States"""
        return sorted(states, reverse=True)[0]
