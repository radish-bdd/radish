# -*- coding: utf-8 -*-

"""
    This module contains a class to load the step and terrain files
"""

import os
import sys
import fnmatch

from . import utils

from .compat import string_types
from .compat import is_nonstr_iter

from .exceptions import RadishError


def load_modules(location):
    """
        Loads all modules in the `location` folder
    """
    location = os.path.expanduser(os.path.expandvars(location))
    if not os.path.exists(location):
        raise OSError("Location '{0}' to load modules does not exist".format(location))

    for p, _, f in os.walk(location):
        for filename in fnmatch.filter(f, "*.py"):
            load_module(os.path.join(p, filename))


def load_module(path):
    """
        Loads a module by the given `path`

        :param string path: the path to the module to load
    """
    parent = os.path.dirname(utils.expandpath(path))
    sys.path.insert(0, parent)
    module_name = os.path.splitext(os.path.split(path)[1])[0]
    try:
        __import__(module_name)
    except Exception as e:
        # raise ImportError("Unable to import module '{0}' from '{1}': {2}".format(module_name, path, e))
        raise e
    finally:
        sys.path.remove(parent)


def load_module_asset(asset):
    """
        Load given asset a python file or a folder of python file

        :param asset: path to folder or file
        :type asset: str
    """
    if os.path.isfile(asset):
        load_module(asset)
    elif os.path.isdir(asset):
        load_modules(asset)


def load_module_assets(assets):
    """
        Load module assets.

        :param assets:
          Asset can be on of the following:
           - path to folder or file
           - iterable of above
        :type assets: str, iterable

        In the future we are hoping to support a dotted module notation as well

        :raises RadishError:
            if unable to identify what to use to load the asset
    """

    # check if asset is a string
    if isinstance(assets, string_types):
        load_module_asset(assets)
    elif is_nonstr_iter(assets):
        for asset in assets:
            load_module_asset(assets)
    else:
        raise RadishError("Could not identify asset type: %s" % asset)
