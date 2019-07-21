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
    SKIPPED = 1
    PENDING = 2
    PASSED = 3
    FAILED = 4
