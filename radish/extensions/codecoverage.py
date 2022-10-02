# -*- coding: utf-8 -*-

"""
This module provides a radish extension to make
coverage measurements.
"""

import sys
import re

from io import StringIO

from radish.extensionregistry import extension
from radish.hookregistry import before, after
from radish.terrain import world
from radish.exceptions import RadishError


@extension
class CodeCoverage(object):
    """
    Code Coverage radish extension
    """

    OPTIONS = [
        ("--with-coverage", "enable code coverage"),
        ("--cover-packages=<cover_packages>", "specify source code package"),
        ("--cover-append", "append coverage data to previous collected data"),
        (
            "--cover-config-file=<cover_config_file>",
            "specify coverage config file [default: .coveragerc]",
        ),
        ("--cover-branches", "include branch coverage in report"),
        ("--cover-erase", "erase previously collected coverage data"),
        (
            "--cover-min-percentage=<cover_min_percentage>",
            "fail if the given minimum coverage percentage is not reached",
        ),
        (
            "--cover-html=<cover_html_dir>",
            "specify a directory where to store HTML coverage report",
        ),
        (
            "--cover-xml=<cover_xml_file>",
            "specify a file where to store XML coverage report",
        ),
    ]
    LOAD_IF = staticmethod(lambda config: config.with_coverage)
    LOAD_PRIORITY = 70

    def __init__(self):
        try:
            from coverage import Coverage
        except ImportError:
            raise RadishError(
                'if you want to use the code coverage you have to "pip install radish-bdd[coverage]"'
            )

        before.all(self.coverage_start)
        after.all(self.coverage_stop)

        if world.config.cover_packages:
            self.cover_packages = world.config.cover_packages.split(",")
        else:
            self.cover_packages = []

        self.coverage = None
        self.modules_on_init = set(sys.modules.keys())

    def coverage_start(self, features, marker):
        """
        Start the coverage measurement
        """
        from coverage import Coverage

        # if no explicit modules are specified we just
        # use the ones loaded from radish's basedir.
        # During the plugin init the basedir modules are
        # not loaded yet, but they are during the start method.
        # Thus, we are safe to consider the difference between the
        # two for coverage measurement.
        if not self.cover_packages:
            source = list(set(sys.modules.keys()).difference(self.modules_on_init))
        else:
            source = self.cover_packages

        self.coverage = Coverage(
            source=source,
            config_file=world.config.cover_config_file,
            branch=world.config.cover_branches,
        )
        if world.config.cover_erase:
            self.coverage.combine()
            self.coverage.erase()

        if world.config.cover_append:
            self.coverage.load()
        self.coverage.start()

    def coverage_stop(self, features, marker):
        """
        Stop the coverage measurement
        and create report
        """
        self.coverage.stop()
        self.coverage.combine()
        self.coverage.save()
        self.coverage.report(file=sys.stdout)

        if world.config.cover_html:
            self.coverage.html_report(directory=world.config.cover_html)

        if world.config.cover_xml:
            self.coverage.xml_report(outfile=world.config.cover_xml)

        if world.config.cover_min_percentage:
            report = StringIO()
            self.coverage.report(file=report)
            match = re.search(r"^TOTAL\s+(.*)$", report.getvalue(), re.MULTILINE)
            if not match:
                raise RadishError("Failed to find total percentage in coverage report")

            total_percentage = int(match.groups()[0].split()[-1][:-1])
            if total_percentage < int(world.config.cover_min_percentage):
                raise RadishError(
                    "Failed to reach minimum expected coverage of {0}% (reached: {1}%)".format(
                        world.config.cover_min_percentage, total_percentage
                    )
                )
