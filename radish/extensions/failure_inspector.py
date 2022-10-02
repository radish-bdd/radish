# -*- coding: utf-8 -*-

"""
This module provides an extension which starts a python shell after a step failed
"""

from radish.hookregistry import after
from radish.stepmodel import Step
from radish.exceptions import RadishError
from radish.extensionregistry import extension


@extension
class FailureInspector(object):
    """
    Failure inspector radish extension
    """

    OPTIONS = [("--inspect-after-failure", "start python shell after failure")]
    LOAD_IF = staticmethod(lambda config: config.inspect_after_failure)
    LOAD_PRIORITY = 10

    def __init__(self):
        after.each_step(self.failure_inspector)

    def failure_inspector(self, step):
        """
        Starts a python shell after a step failed
        """
        if step.state is not Step.State.FAILED:
            return

        try:
            from IPython import embed
        except ImportError as e:
            raise RadishError(
                'if you want to use the failure inspector extension you have to "pip install radish-bdd[ipython-debugger]"'
            )

        embed()
