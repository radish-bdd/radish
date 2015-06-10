# -*- coding: utf-8 -*-

"""
    This module provides an extension to write all features, scenarios and steps to the syslog.
"""


from radish.scenariooutline import ScenarioOutline
from radish.terrain import before, after

import syslog


def get_scenario_feature(scenario):
    """
        Gets the scenarios feature
    """
    if isinstance(scenario.parent, ScenarioOutline):
        return scenario.parent.parent

    return scenario.parent


@before.all  # pylint: disable=no-member
def syslog_writer_before_all(features, marker):  # pylint: disable=unused-argument
    """
        Opens the syslog
    """
    syslog.openlog("radish")


@after.all  # pylint: disable=no-member
def syslog_writer_after_all(features, marker):  # pylint: disable=unused-argument
    """
        Closes the syslog
    """
    syslog.closelog()


@before.each_feature  # pylint: disable=no-member
def syslog_writer_before_each_feature(feature):
    """
        Writes the feature to the syslog
    """
    syslog.syslog(syslog.LOG_INFO, "testing feature {}".format(feature.id))


@after.each_feature  # pylint: disable=no-member
def syslog_writer_after_each_feature(feature):
    """
        Writes the feature to the syslog
    """
    syslog.syslog(syslog.LOG_INFO, "finished feature {}".format(feature.id))


@before.each_scenario  # pylint: disable=no-member
def syslog_writer_before_each_scenario(scenario):
    """
        Writes the scenario to the syslog
    """
    syslog.syslog(syslog.LOG_INFO, "testing scenario {}.{}".format(get_scenario_feature(scenario).id, scenario.id))


@after.each_scenario  # pylint: disable=no-member
def syslog_writer_after_each_scenario(scenario):
    """
        Writes the scenario to the syslog
    """
    syslog.syslog(syslog.LOG_INFO, "finished scenario {}.{}".format(get_scenario_feature(scenario).id, scenario.id))


@before.each_step  # pylint: disable=no-member
def syslog_writer_before_each_step(step):
    """
        Writes the step to the syslog
    """
    syslog.syslog(syslog.LOG_INFO, "testing step {}.{}.{}".format(get_scenario_feature(step.parent).id, step.parent.id, step.id))


@after.each_step  # pylint: disable=no-member
def syslog_writer_after_each_step(step):
    """
        Writes the step to the syslog
    """
    syslog.syslog(syslog.LOG_INFO, "{} step {}.{}.{}".format(step.state, get_scenario_feature(step.parent).id, step.parent.id, step.id))
