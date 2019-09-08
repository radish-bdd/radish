"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


import threading

world = threading.local()
world.__doc__ = """Thread-local radish contex object

This object can be used to attach arbitrary data like
variables, functions and other objects which
can be accessed later in Step Implementations and Hooks.

However, it's preferred to use scoped contexts
like :attr:`radish.Step.context`, :attr:`Scenario.context`
or :attr:`Feature.context` for data.
"""


def pick(func):
    """Add the given function to the ``world`` object

    This can be used to easier access helper functions in Steps and Hooks.
    """
    setattr(world, func.__name__, func)
    return func


world.pick = pick
