"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.loader import load_modules, load_module
from radish.errors import RadishError


def test_loader_should_raise_if_location_to_load_not_exists(mocker):
    """The Loader should raise an Exception if a location does not exist which should be loaded"""
    # given
    non_existant_location = mocker.MagicMock()
    non_existant_location.exists.return_value = False
    locations = [mocker.MagicMock(), non_existant_location]

    # then
    with pytest.raises(RadishError):
        # when
        load_modules(locations)


def test_loader_should_load_python_module_in_location(mocker):
    """The Loader should attempt to load Python module within a location"""
    # given
    load_module_mock = mocker.patch("radish.loader.load_module")
    module_mock = mocker.MagicMock(name="Python Module")
    location = mocker.MagicMock()
    location.glob.return_value = [module_mock]

    # when
    loaded_locations = load_modules([location])

    # then
    load_module_mock.assert_called_once_with(module_mock)
    assert loaded_locations == [module_mock]


def test_loader_should_fail_when_import_fails(mocker):
    """The Loader should fail if the import of a module fails"""
    # given
    spec_mock = mocker.patch("importlib.util.spec_from_file_location")
    spec_mock.return_value.loader.exec_module.side_effect = Exception("buuhu!")
    mocker.patch("importlib.util.module_from_spec")
    location = mocker.MagicMock("Python Module Path")
    location.stem = "foo"

    # then
    with pytest.raises(ImportError, match="Unable to import module 'foo' .*: buuhu!"):
        # when
        load_module(location)
