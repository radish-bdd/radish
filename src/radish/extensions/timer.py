"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.models.timed import Timed
from radish.hookregistry import before, after


def record_starttime(timed_model: Timed):
    """Record the start time for the given Model"""
    timed_model.record_starttime()


def record_endtime(timed_model: Timed):
    """Record the end time for the given Model"""
    timed_model.record_endtime()


before.each_feature()(lambda f: record_starttime(f))
before.each_scenario()(lambda f: record_starttime(f))
before.each_step()(lambda f: record_starttime(f))
after.each_feature()(lambda f: record_endtime(f))
after.each_scenario()(lambda f: record_endtime(f))
after.each_step()(lambda f: record_endtime(f))
