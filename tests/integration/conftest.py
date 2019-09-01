"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import subprocess


import pytest


@pytest.fixture(name="radish_runner")
def setup_radish_runner(tmpdir):
    """Fixture to setup a radish command line runner"""

    def __runner(features, basedir, radish_args):
        cmdline = ["radish", *features, "-b", basedir, *radish_args]
        proc = subprocess.Popen(
            cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(tmpdir)
        )
        stdout, stderr = proc.communicate()
        return proc.returncode, stdout, stderr

    return __runner
