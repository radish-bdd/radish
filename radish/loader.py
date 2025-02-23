"""
This module contains a class to load the step and terrain files
"""

import fnmatch
import os


def load_modules(location):
    """
    Loads all modules in the `location` folder
    """
    if os.name == "nt":
        location = location.replace("$PWD", os.getcwd())

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
    module_name = os.path.splitext(os.path.split(path)[1])[0]
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        raise ImportError("Unable to import module '{0}' from '{1}': {2}".format(module_name, path, e))
