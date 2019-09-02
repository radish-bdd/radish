"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import re
import sys
from io import StringIO

import click

from radish.errors import RadishError
from radish.extensionregistry import extension
from radish.hookregistry import before, after


@extension
class Coverage:
    """
    Extension for Python Code Coverage
    """

    OPTIONS = [
        click.Option(
            param_decls=("--with-coverage", "with_coverage"),
            is_flag=True,
            help="Enable Code Coverage",
        ),
        click.Option(
            param_decls=("--cover-package", "cover_packages"),
            multiple=True,
            help="Python Package name for which the coverage is measured and reported",
        ),
        click.Option(
            param_decls=("--cover-append", "cover_append"),
            is_flag=True,
            help="Append measured coverage data to previous collected data",
        ),
        click.Option(
            param_decls=("--cover-config-file", "cover_config_file"),
            default=".coveragerc",
            help="Path to a custom coverage configuration file",
        ),
        click.Option(
            param_decls=("--cover-branches", "cover_branches"),
            is_flag=True,
            help="Include branch coverage in the report",
        ),
        click.Option(
            param_decls=("--cover-erase", "cover_erase"),
            is_flag=True,
            help="Erase previously collected data",
        ),
        click.Option(
            param_decls=("--cover-min-percentage", "cover_min_percentage"),
            type=click.IntRange(0, 100),
            help="Fail if the provided minimum coverage percentage is not reached",
        ),
        click.Option(
            param_decls=("--cover-html", "cover_html"),
            help="Path to the directory where to store the HTML coverage report",
        ),
        click.Option(
            param_decls=("--cover-xml", "cover_xml"),
            help="Path to the directory where to store the XML coverage report",
        ),
    ]

    @classmethod
    def load(cls, config):
        if config.with_coverage:
            return cls(
                config.cover_packages,
                config.cover_append,
                config.cover_config_file,
                config.cover_branches,
                config.cover_erase,
                config.cover_min_percentage,
                config.cover_html,
                config.cover_xml,
            )
        else:
            return None

    def __init__(
        self,
        cover_packages,
        cover_append,
        cover_config_file,
        cover_branches,
        cover_erase,
        cover_min_percentage,
        cover_html,
        cover_xml,
    ):
        try:
            from coverage import Coverage  # noqa
        except ImportError:
            raise RadishError(
                "if you want to use the code coverage extension you have to "
                "'pip install radish-bdd[coverage]'"
            )

        self.cover_packages = cover_packages
        self.cover_append = cover_append
        self.cover_config_file = cover_config_file
        self.cover_branches = cover_branches
        self.cover_erase = cover_erase
        self.cover_min_percentage = cover_min_percentage
        self.cover_html = cover_html
        self.cover_xml = cover_xml

        before.all()(self.coverage_start)
        after.all()(self.coverage_stop)

        self.coverage = None
        self.modules_on_init = set(sys.modules.keys())

    def coverage_start(self, features):
        """
        Hook to start the coverage measurement
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
            config_file=self.cover_config_file,
            branch=self.cover_branches,
        )
        if self.cover_erase:
            self.coverage.combine()
            self.coverage.erase()

        if self.cover_append:
            self.coverage.load()
        self.coverage.start()

    def coverage_stop(self, features):
        """
        Stop the coverage measurement
        and create report
        """
        self.coverage.stop()
        self.coverage.combine()
        self.coverage.save()
        self.coverage.report(file=sys.stdout)

        if self.cover_html:
            self.coverage.html_report(directory=self.cover_html)

        if self.cover_xml:
            self.coverage.xml_report(outfile=self.cover_xml)

        if self.cover_min_percentage:
            report = StringIO()
            self.coverage.report(file=report)
            match = re.search(r"^TOTAL\s+(.*)$", report.getvalue(), re.MULTILINE)
            if not match:
                raise RadishError("Failed to find total percentage in coverage report")

            total_percentage = int(match.groups()[0].split()[-1][:-1])
            if total_percentage < int(self.cover_min_percentage):
                raise RadishError(
                    "Failed to reach minimum expected coverage of {0}% (reached: {1}%)".format(
                        self.cover_min_percentage, total_percentage
                    )
                )
