"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

import radish.utils as utils


@pytest.mark.filterwarnings("ignore")
def test_getting_any_debugger():
    """When asking for a debugger it should return one

    It shouldn't matter if IPython is installed or not,
    just give me that debugger.
    """
    # when
    debugger = utils.get_debugger()

    # then
    assert callable(debugger.runcall)


def test_utils_should_locate_arbitrary_python_object():
    # when
    obj = utils.locate_python_object("str")

    # then
    assert obj == str


def test_converting_pos_args_into_kwargs():
    # given
    def func(_, arg1, arg2, kwarg1=1, kwargs2=2):
        pass

    pos_arg_values = ["arg1-value", "arg2-value"]

    # when
    kwargs = utils.get_func_pos_args_as_kwargs(func, pos_arg_values)

    # then
    assert kwargs == {"arg1": "arg1-value", "arg2": "arg2-value"}
