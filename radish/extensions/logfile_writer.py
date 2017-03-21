# -*- coding: utf-8 -*-

"""
    This module provides an extension to write all features, scenarios and steps to a log file.
"""

import os
from radish.terrain import world
from radish.feature import Feature
from radish.hookregistry import before, after
from radish.extensionregistry import extension


@extension
class LogFileWriter(object):
    """
        Extension to write a log file. It is supported by every platform.
        It will write the same content as the syslog extension but into a
        file.
    """

    OPTIONS = [("--log=<logfile>", "log all of your features, scenarios, and steps to a log file")]
    LOAD_IF = staticmethod(lambda config: config.log)
    LOAD_PRIORITY = 80

    def __init__(self):
        before.all(self.logfile_writer_before_all)
        before.each_feature(self.logfile_writer_before_each_feature)
        before.each_scenario(self.logfile_writer_before_each_scenario)
        before.each_step(self.logfile_writer_before_each_step)
        after.all(self.logfile_writer_after_all)
        after.each_feature(self.logfile_writer_after_each_feature)
        after.each_scenario(self.logfile_writer_after_each_scenario)
        after.each_step(self.logfile_writer_after_each_step)

    def get_scenario_feature(self, scenario):
        """
            Gets the scenarios feature
        """
        if not isinstance(scenario.parent, Feature):
            return scenario.parent.parent

        return scenario.parent

    def log(self, message):
        """
            Logs the given message to a log file

            :param string message: the message to log
        """
        with open(world.config.log, "a+") as f:
            f.write("%s%s" % (message, os.linesep))

    def logfile_writer_before_all(self, features, marker):  # pylint: disable=unused-argument
        """
            Write the begin message
        """
        self.log(u"begin run {0}".format(marker))

    def logfile_writer_after_all(self, features, marker):  # pylint: disable=unused-argument
        """
            Write the end message
        """
        self.log(u"end run {0}".format(marker))

    def logfile_writer_before_each_feature(self, feature):
        """
            Writes the feature to a log file
        """
        self.log(u"begin feature {0}:{1} {2}".format(world.config.marker, feature.id, feature.sentence))

    def logfile_writer_after_each_feature(self, feature):
        """
            Writes the feature to a log file
        """
        self.log(u"end feature {0}:{1} {2}".format(world.config.marker, feature.id, feature.sentence))

    def logfile_writer_before_each_scenario(self, scenario):
        """
            Writes the scenario to a log file
        """
        self.log(u"begin scenario {0}:{1}.{2} {3}".format(world.config.marker, self.get_scenario_feature(scenario).id,
                                                          scenario.id, scenario.sentence))

    def logfile_writer_after_each_scenario(self, scenario):
        """
            Writes the scenario to a log file
        """
        self.log(u"end scenario {0}:{1}.{2} {3}".format(world.config.marker, self.get_scenario_feature(scenario).id,
                                                        scenario.id, scenario.sentence))

    def logfile_writer_before_each_step(self, step):
        """
            Writes the step to a log file
        """
        self.log(
            u"begin step {0}:{1}.{2}.{3} {4}".format(world.config.marker, self.get_scenario_feature(step.parent).id,
                                                     step.parent.id, step.id, step.sentence))

    def logfile_writer_after_each_step(self, step):
        """
            Writes the step to a log file
        """
        self.log(u"{0} step {1}:{2}.{3}.{4} {5}".format(step.state, world.config.marker,
                                                        self.get_scenario_feature(step.parent).id, step.parent.id,
                                                        step.id, step.sentence))
