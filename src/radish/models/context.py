"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class Context:
    """Represents a Context object for arbitrary data

    A ``Context`` object can be used by other models to
    store arbirtrary data during it's lifetime.
    """

    def __init__(self):
        self.constants = []
