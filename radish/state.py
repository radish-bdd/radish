"""
    This module provides a class to represent State
"""

from enum import Enum


class State(str, Enum):
    """
        Represents the state of a Step, scenario, feature
    """
    UNTESTED = "untested"
    SKIPPED = "skipped"
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
