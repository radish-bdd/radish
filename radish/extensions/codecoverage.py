# -*- coding: utf-8 -*-

"""
This module provides a radish extension to make
coverage measurements.
"""

import sys

from coverage import Coverage

from radish.extensionregistry import extension
from radish.hookregistry import before, after
from radish.terrain import world


@extension
class CodeCoverage(object):
    """
        Code Coverage radish extension
    """
    OPTIONS = [
        ('--with-coverage', 'enable code coverage'),
        ('--cover-packages=<cover_packages>', 'specify source code package'),
        ('--cover-append', 'append coverage data to previous collected data')
    ]
    LOAD_IF = staticmethod(lambda config: config.with_coverage)
    LOAD_PRIORITY = 70

    def __init__(self):
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

        self.coverage = Coverage(source=source)
        if world.config.cover_append:
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
