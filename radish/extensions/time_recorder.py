# -*- coding: utf-8 -*-

"""
    This module is a REQUIRED extension to record the time of Features, Scenarios and Steps
"""

from datetime import datetime

from radish.hookregistry import after, before
from radish.extensionregistry import extension

__REQUIRED__ = True

@extension
class TimeRecorder(object):
    """
        Time Recorder radish plugin
    """
    LOAD_IF = staticmethod(lambda config: not config.show)
    LOAD_PRIORITY = 1

    def __init__(self):
        before.each_feature(self.time_recorder_before_each_feature)
        before.each_scenario(self.time_recorder_before_each_scenario)
        before.each_step(self.time_recorder_before_each_step)
        after.each_feature(self.time_recorder_after_each_feature)
        after.each_scenario(self.time_recorder_after_each_scenario)
        after.each_step(self.time_recorder_after_each_step)

    def time_recorder_before_each_feature(self, feature):
        """
            Sets the starttime of the feature
        """
        feature.starttime = datetime.now()

    def time_recorder_before_each_scenario(self, scenario):
        """
            Sets the starttime of the scenario
        """
        scenario.starttime = datetime.now()


    def time_recorder_before_each_step(self, step):
        """
            Sets the starttime of the step
        """
        step.starttime = datetime.now()

    def time_recorder_after_each_feature(self, feature):
        """
            Sets the endtime of the feature
        """
        feature.endtime = datetime.now()

    def time_recorder_after_each_scenario(self, scenario):
        """
            Sets the endtime of the scenario
        """
        scenario.endtime = datetime.now()

    def time_recorder_after_each_step(self, step):
        """
            Sets the endtime of the step
        """
        step.endtime = datetime.now()
