"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import time
from datetime import timedelta


class Timed:
    """Base-Class with can be used to record a start- and end time on an instance"""

    def __init__(self):
        self.starttime = None
        self.endtime = None

    def record_starttime(self):
        self.starttime = time.time()

    def record_endtime(self):
        self.endtime = time.time()

    def duration(self):
        """Get the current duration.

        If no ``self.endtime`` is set the duration
        is until the current time.
        """
        if self.starttime is None:
            return timedelta(0)

        if self.endtime is None:
            return timedelta(seconds=time.time() - self.starttime)

        return timedelta(seconds=self.endtime - self.starttime)
