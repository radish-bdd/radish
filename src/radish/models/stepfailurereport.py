"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import sys
import traceback


class StepFailureReport:
    """Represents a Failure Report for a single Step"""

    def __init__(self, exception):
        self.exception = exception
        self.reason = str(exception)
        self.traceback = str(traceback.format_exc())
        self.name = exception.__class__.__name__
        traceback_info = traceback.extract_tb(sys.exc_info()[2])[-1]
        self.filename = traceback_info[0]
        self.line = int(traceback_info[1])
