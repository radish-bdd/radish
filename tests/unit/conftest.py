# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import os

import pytest

from radish.terrain import world
from radish.core import Core, Configuration
from radish.parser import FeatureParser

#: Holds the path to the Feature file resources
__FEATURE_FILES_DIR__ = os.path.join(os.path.dirname(__file__), 'features')


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


@pytest.fixture()
def core():
    """
    Fixture to radish.core.Core
    """
    return Core()


@pytest.fixture()
def featurefile(request):
    """
    Fixture to get the path to a Feature File
    """
    featurename = request.param[0]
    return os.path.join(__FEATURE_FILES_DIR__, featurename + '.feature')


@pytest.fixture()
def parser(request, core):
    """
    Fixture to create a Feature Parser ready to parse the given Feature File
    """
    featurename = request.param[0]
    # get parser positional arguments
    try:
        parser_args = request.param[1]
    except IndexError:
        parser_args = []
    # get parser keyword arguments
    try:
        parser_kwargs = request.param[2]
    except IndexError:
        parser_kwargs = {}

    # create the Feature Parser instance
    return FeatureParser(core, os.path.join(__FEATURE_FILES_DIR__, featurename + '.feature'),
                         1, *parser_args, **parser_kwargs)
