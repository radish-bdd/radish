"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


import threading

world = threading.local()


def pick(func):
    """Add the given function to the ``world`` object

    This can be used to easier access helper functions in Steps and Hooks.
    """
    setattr(world, func.__name__, func)
    return func


world.pick = pick
