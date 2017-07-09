# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.terrain import world
from radish.core import Configuration


@pytest.fixture(scope='function', autouse=True)
def mock_world_config():
    """
    Fixture to mock the terrain.world.config object
    with some default fake data.
    """
    # default command line arguments
    arguments = {
        '--basedir': ['$PWD/radish'],
        '--bdd-xml': None,
        '--cover-append': False,
        '--cover-branches': False,
        '--cover-config-file': '.coveragerc',
        '--cover-erase': False,
        '--cover-html': None,
        '--cover-min-percentage': None,
        '--cover-packages': None,
        '--cover-xml': None,
        '--cucumber-json': None,
        '--debug-after-failure': False,
        '--debug-steps': False,
        '--dry-run': False,
        '--early-exit': False,
        '--expand': False,
        '--help': False,
        '--inspect-after-failure': False,
        '--marker': 'time.time()',
        '--no-ansi': False,
        '--no-line-jump': False,
        '--profile': None,
        '--scenarios': None,
        '--shuffle': False,
        '--syslog': False,
        '--tags': None,
        '--user-data': [],
        '--version': False,
        '--with-coverage': False,
        '--with-traceback': False,
        '--write-ids': False,
        '--write-steps-once': False,
        '<features>': ['features/'],
        'show': False
    }
    world.config = Configuration(arguments)
    yield
    delattr(world, 'config')


@pytest.fixture()
def mock_utils_debugger(mocker):
    """
    Fixture to mock the pdf Python debugger
    """
    def call_orig_func(func, *args, **kwargs):
        """
        Helper to mock pdf.runcall interface
        """
        return func(*args, **kwargs)


    debugger_mock = mocker.patch('radish.utils.get_debugger')
    debugger_mock.return_value.runcall = mocker.MagicMock(side_effect=call_orig_func)
    return debugger_mock.return_value
