"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class RadishError(Exception):
    """Base-Exception for all radish based errors."""

    pass


class StepImplementationNotFoundError(RadishError):
    """Exception raised when no Step Implementation can be found for a Step"""

    def __init__(self, step):
        self.step = step


class StepImplementationPatternNotSupported(RadishError):
    """
    Exception raised when a registered Step Implementation Pattern is not supported by any matcher
    """

    def __init__(self, step_impl):
        self.step_impl = step_impl
