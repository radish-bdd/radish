# -*- coding: utf-8 -*-

"""
    This module provides a radish extension to make
    coverage measurements.
"""


from radish.extensionregistry import extension
from radish.hookregistry import before, after
from radish.terrain import world

import sys
from coverage import Coverage


@extension
class CodeCoverage(object):
    """
        Code Coverage radish extension
    """
    OPTIONS = [
        ("--with-coverage", "enable code coverage"),
        ("--cover-packages=<cover_packages>", "specify source code package")
    ]
    LOAD_IF = staticmethod(lambda config: config.with_coverage)
    LOAD_PRIORITY = 70

    def __init__(self):
        before.all(self.coverage_start)
        after.all(self.coverage_stop)

        if world.config.cover_packages:
            cover_packages = world.config.cover_packages.split(",")
        else:
            cover_packages = []
        self.coverage = Coverage(source=cover_packages)

    def coverage_start(self, features, marker):
        """
            Start the coverage measurement
        """
        self.coverage.load()
        self.coverage.start()

    def coverage_stop(self, features, marker):
        """
            Stop the coverage measurement
            and create report
        """
        self.coverage.stop()
        self.coverage.save()
        self.coverage.report(file=sys.stdout)
