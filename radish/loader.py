# -*- coding: utf-8 -*-

"""
    This module contains a class to load the step and terrain files
"""

import os
import sys
import fnmatch

from . import utils


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
        #raise ImportError("Unable to import module '{0}' from '{1}': {2}".format(module_name, path, e))
        raise e
    finally:
        sys.path.remove(parent)
