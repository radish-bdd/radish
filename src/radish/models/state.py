"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from enum import Enum


class State(Enum):
    """Represents the State of other models"""

    UNTESTED = 0
    RUNNING = 1
    SKIPPED = 2
    PENDING = 3
    PASSED = 4
    FAILED = 5
