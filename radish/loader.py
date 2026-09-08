"""
This module contains a class to load the step and terrain files
"""

import fnmatch
import os


def load_modules(location, loaded_files=None):
    """
    Loads all modules in the `location` folder

    :param str location: the base directory to recursively load modules from
    :param set[tuple[int, int]] loaded_files: device and inode nr of files already
        loaded from another directory, used to avoid loading the same file twice.
    """
    if loaded_files is None:
        loaded_files = set()

    if os.name == "nt":
        location = location.replace("$PWD", os.getcwd())

    location = os.path.expanduser(os.path.expandvars(location))
    if not os.path.exists(location):
        raise OSError("Location '{}' to load modules does not exist".format(location))

    for p, _, f in os.walk(location):
        for filename in fnmatch.filter(f, "*.py"):
            path = os.path.join(p, filename)
            stat = os.stat(path)
            file_id = (stat.st_dev, stat.st_ino)
            if file_id in loaded_files:
                continue
            loaded_files.add(file_id)
            load_module(path)


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
        raise ImportError("Unable to import module '{}' from '{}': {}".format(module_name, path, e))
