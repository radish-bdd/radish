# -*- coding: utf-8 -*-

"""
This module provides an extension to write all features, scenarios and steps to the syslog.
"""

from radish.terrain import world
from radish.feature import Feature
from radish.hookregistry import before, after
from radish.extensionregistry import extension


@extension
class SyslogWriter(object):
    """
    Syslog Writer radish extension. This extension is only supported on
    systems where the Python standard library supports the system logger
    (syslog). For example, this extension works on UNIX and UNIX-like
    systems (Linux), but will not work on Windows.
    """

    OPTIONS = [
        ("--syslog", "log all of your features, scenarios, and steps to the syslog")
    ]
    LOAD_IF = staticmethod(lambda config: config.syslog)
    LOAD_PRIORITY = 40

    def __init__(self):
        # import syslog only if the extension got loaded
        # but not if the module got loaded.
        import syslog

        before.all(self.syslog_writer_before_all)
        before.each_feature(self.syslog_writer_before_each_feature)
        before.each_scenario(self.syslog_writer_before_each_scenario)
        before.each_step(self.syslog_writer_before_each_step)
        after.all(self.syslog_writer_after_all)
        after.each_feature(self.syslog_writer_after_each_feature)
        after.each_scenario(self.syslog_writer_after_each_scenario)
        after.each_step(self.syslog_writer_after_each_step)

    def get_scenario_feature(self, scenario):
        """
            Gets the scenarios feature
        """
        if not isinstance(scenario.parent, Feature):
            return scenario.parent.parent

        return scenario.parent

    def log(self, message):
        """
        Logs the given message to the syslog

        :param string message: the message to log
        """
        import syslog

        try:
            if isinstance(message, unicode):
                message = message.encode("utf8")
        except Exception:  # pylint: disable=broad-except
            pass
        finally:
            syslog.syslog(syslog.LOG_INFO, message)

    def syslog_writer_before_all(
        self, features, marker
    ):  # pylint: disable=unused-argument
        """
        Opens the syslog
        """
        import syslog

        syslog.openlog(b"radish")
        self.log("begin run {0}".format(marker))

    def syslog_writer_after_all(
        self, features, marker
    ):  # pylint: disable=unused-argument
        """
        Closes the syslog
        """
        import syslog

        self.log("end run {0}".format(marker))
        syslog.closelog()

    def syslog_writer_before_each_feature(self, feature):
        """
        Writes the feature to the syslog
        """
        self.log(
            "begin feature {0}:{1} {2}".format(
                world.config.marker, feature.id, feature.sentence
            )
        )

    def syslog_writer_after_each_feature(self, feature):
        """
        Writes the feature to the syslog
        """
        self.log(
            "end feature {0}:{1} {2}".format(
                world.config.marker, feature.id, feature.sentence
            )
        )

    def syslog_writer_before_each_scenario(self, scenario):
        """
        Writes the scenario to the syslog
        """
        self.log(
            "begin scenario {0}:{1}.{2} {3}".format(
                world.config.marker,
                self.get_scenario_feature(scenario).id,
                scenario.id,
                scenario.sentence,
            )
        )

    def syslog_writer_after_each_scenario(self, scenario):
        """
        Writes the scenario to the syslog
        """
        self.log(
            "end scenario {0}:{1}.{2} {3}".format(
                world.config.marker,
                self.get_scenario_feature(scenario).id,
                scenario.id,
                scenario.sentence,
            )
        )

    def syslog_writer_before_each_step(self, step):
        """
        Writes the step to the syslog
        """
        self.log(
            "begin step {0}:{1}.{2}.{3} {4}".format(
                world.config.marker,
                self.get_scenario_feature(step.parent).id,
                step.parent.id,
                step.id,
                step.sentence,
            )
        )

    def syslog_writer_after_each_step(self, step):
        """
        Writes the step to the syslog
        """
        self.log(
            "{0} step {1}:{2}.{3}.{4} {5}".format(
                step.state,
                world.config.marker,
                self.get_scenario_feature(step.parent).id,
                step.parent.id,
                step.id,
                step.sentence,
            )
        )
