# -*- coding: utf-8 -*-

"""
    This module is a REQUIRED extension to record the time of Features, Scenarios and Steps
"""

from datetime import datetime

from radish.hookregistry import after, before

__REQUIRED__ = True


@before.each_feature  # pylint: disable=no-member
def time_recorder_before_each_feature(feature):
    """
        Sets the starttime of the feature
    """
    feature.starttime = datetime.now()


@before.each_scenario  # pylint: disable=no-member
def time_recorder_before_each_scenario(scenario):
    """
        Sets the starttime of the scenario
    """
    scenario.starttime = datetime.now()


@before.each_step  # pylint: disable=no-member
def time_recorder_before_each_step(step):
    """
        Sets the starttime of the step
    """
    step.starttime = datetime.now()


@after.each_feature  # pylint: disable=no-member
def time_recorder_after_each_feature(feature):
    """
        Sets the endtime of the feature
    """
    feature.endtime = datetime.now()


@after.each_scenario  # pylint: disable=no-member
def time_recorder_after_each_scenario(scenario):
    """
        Sets the endtime of the scenario
    """
    scenario.endtime = datetime.now()


@after.each_step  # pylint: disable=no-member
def time_recorder_after_each_step(step):
    """
        Sets the endtime of the step
    """
    step.endtime = datetime.now()
