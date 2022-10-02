# -*- coding: utf-8 -*-

"""
This module provides an extension which starts a debugger when a step fails
"""

from radish.hookregistry import after
from radish.stepmodel import Step
from radish.extensionregistry import extension
import radish.utils as utils


@extension
class FailureDebugger(object):
    """
    Failure debugger radish extension
    """

    OPTIONS = [("--debug-after-failure", "start python debugger after failure")]
    LOAD_IF = staticmethod(lambda config: config.debug_after_failure)
    LOAD_PRIORITY = 20

    def __init__(self):
        after.each_step(self.failure_debugger)

    def failure_debugger(self, step):
        """
        Starts a python debugger if the step failed
        """
        if step.state is not Step.State.FAILED:
            return

        pdb = utils.get_debugger()
        pdb.set_trace()
