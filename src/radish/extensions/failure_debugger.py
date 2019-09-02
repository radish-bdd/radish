"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import click

from radish.utils import get_debugger
from radish.extensionregistry import extension
from radish.hookregistry import after
from radish.models.state import State


@extension
class FailureDebugger:
    """
    Extension to start a debugger upon a Step failure
    """

    OPTIONS = [
        click.Option(
            param_decls=("--debug-after-failure", "debug_after_failure"),
            is_flag=True,
            help="Start a Python debugger when a Step failed",
        )
    ]

    @classmethod
    def load(cls, config):
        if config.debug_after_failure:
            return cls()
        else:
            return None

    def __init__(self):
        after.each_step()(failure_debugger)


def failure_debugger(self, step):
    """Start the Python debugger after a Step failure"""
    if step.state is not State.FAILED:
        return

    pdb = get_debugger()
    pdb.set_trace()
