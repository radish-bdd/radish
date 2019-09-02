"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import click

from radish.extensionregistry import extension
from radish.hookregistry import before, after


@extension
class SyslogWriter:
    """Syslog Writer radish extension

    This extension is only supported on
    systems where the Python standard library supports the system logger
    (syslog). For example, this extension works on UNIX and UNIX-like
    systems (Linux), but will not work on Windows.
    """

    OPTIONS = [
        click.Option(
            param_decls=("--with-syslog-markers", "with_syslog_markers"),
            is_flag=True,
            help="Log a marker for each Feature, Scenario and Step to the syslog",
        )
    ]

    @classmethod
    def load(cls, config):
        if config.with_syslog_markers:
            return cls(config.marker)
        else:
            return None

    def __init__(self, marker):
        self.marker = marker
        # import syslog only if the extension got loaded
        # but not if the module got loaded.
        import syslog  # noqa

        before.all()(self.syslog_writer_before_all)
        before.each_feature()(self.syslog_writer_before_each_feature)
        before.each_scenario()(self.syslog_writer_before_each_scenario)
        before.each_step()(self.syslog_writer_before_each_step)
        after.all()(self.syslog_writer_after_all)
        after.each_feature()(self.syslog_writer_after_each_feature)
        after.each_scenario()(self.syslog_writer_after_each_scenario)
        after.each_step()(self.syslog_writer_after_each_step)

    def syslog_writer_before_all(self, features):
        import syslog

        syslog.openlog("radish")
        syslog.syslog("begin run {}".format(self.marker))

    def syslog_writer_after_all(self, features):
        import syslog

        syslog.syslog("end run {}".format(self.marker))
        syslog.closelog()

    def syslog_writer_before_each_feature(self, feature):
        import syslog

        syslog.syslog(
            "begin feature {}:{} {}".format(
                self.marker, feature.id, feature.short_description
            )
        )

    def syslog_writer_after_each_feature(self, feature):
        import syslog

        syslog.syslog(
            "end feature {}:{} {}".format(
                self.marker, feature.id, feature.short_description
            )
        )

    def syslog_writer_before_each_scenario(self, scenario):
        import syslog

        syslog.syslog(
            "begin scenario {}:{}.{} {}".format(
                self.marker,
                scenario.feature.id,
                scenario.id,
                scenario.short_description,
            )
        )

    def syslog_writer_after_each_scenario(self, scenario):
        import syslog

        syslog.syslog(
            "end scenario {}:{}.{} {}".format(
                self.marker,
                scenario.feature.id,
                scenario.id,
                scenario.short_description,
            )
        )

    def syslog_writer_before_each_step(self, step):
        import syslog

        syslog.syslog(
            "begin step {}:{}.{}.{} {} {}".format(
                self.marker,
                step.feature.id,
                step.scenario.id,
                step.id,
                step.keyword,
                step.text,
            )
        )

    def syslog_writer_after_each_step(self, step):
        import syslog

        syslog.syslog(
            "{} step {}:{}.{}.{} {} {}".format(
                step.state.name.lower(),
                self.marker,
                step.feature.id,
                step.scenario.id,
                step.id,
                step.keyword,
                step.text,
            )
        )
