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
