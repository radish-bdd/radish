# -*- coding: utf-8 -*-

"""
    This module contains a class to load the step and terrain files
"""

import os
import sys
import fnmatch

from . import utils


class Loader(object):
    """
        Class to load a modules in a given folder
    """
    def __init__(self, location):
        self._location = os.path.expanduser(os.path.expandvars(location))
        self._loaded_modules = {}

    def load_all(self):
        """
            Loads all modules in the `location` folder
        """
        if not os.path.exists(self._location):
            raise OSError("Location '{0}' to load modules does not exist".format(self._location))

        for p, d, f in os.walk(self._location):
            for filename in fnmatch.filter(f, "*.py"):
                self.load_module(os.path.join(p, filename))

    def load_module(self, path):
        """
            Loads a module by the given `path`

            :param string path: the path to the module to load
        """
        parent = os.path.dirname(utils.expandpath(path))
        sys.path.insert(0, parent)
        module_name = os.path.splitext(os.path.split(path)[1])[0]
        try:
            module = __import__(module_name)
        except Exception as e:
            #raise ImportError("Unable to import module '{0}' from '{1}': {2}".format(module_name, path, e))
            raise e
        else:
            self._loaded_modules[module_name] = module
        finally:
            sys.path.remove(parent)
