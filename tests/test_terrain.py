"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.terrain import world


def test_pick_function_into_world_object():
    """
    The world.pick() decroator should be able to assign arbitrary functions to the world object
    """
    # when
    @world.pick
    def some_arbitrary_helper_func(answer):
        return answer == 42

    # then
    assert world.some_arbitrary_helper_func is some_arbitrary_helper_func
