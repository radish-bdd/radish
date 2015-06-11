# -*- coding: utf-8 -*-


"""
    This module provides an extension which starts a debugger when a step fails
"""

from radish.terrain import world
from radish.hookregistry import after
from radish.step import Step
import radish.utils as utils


@after.each_step  # pylint: disable=no-member
def failure_debugger_after_each_step(step):
    """
        Starts a python debugger if the step failed
    """
    if not world.config.debug_after_failure or step.state is not Step.State.FAILED:
        return

    pdb = utils.get_debugger()
    pdb.set_trace()
