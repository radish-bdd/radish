# -*- coding: utf-8 -*-

"""
    This module provides an extension which starts a python shell after a step failed
"""

from radish.terrain import world
from radish.hookregistry import after
from radish.step import Step
from radish.exceptions import RadishError


@after.each_step  # pylint: disable=no-member
def failure_inspector_after_each_step(step):
    """
        Starts a python shell after a step failed
    """
    if not world.config.inspect_after_failure or step.state is not Step.State.FAILED:
        return

    try:
        from IPython import embed
    except ImportError as e:
        raise RadishError("Cannot import IPython embed function: {0}".format(e))

    embed()
