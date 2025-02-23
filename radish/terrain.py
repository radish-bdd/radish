"""
Terrain module providing step overlapping data containers
"""

import threading

world = threading.local()


def pick(func):
    """
    Picks the given function and add it to the world object
    """
    setattr(world, func.__name__, func)
    return func


world.pick = pick
