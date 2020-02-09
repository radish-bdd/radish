"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pydoc
import warnings
from collections import OrderedDict

import yaml


def get_debugger():
    """Return a debugger to debug Steps

    The debugger is evaluated according to the following rules:
    1. Check if IPython is installed, if so, use the IPython Pdb
    2. Use Python's built-in Pdb
    """
    try:
        from IPython.core.debugger import Pdb  # pragma: no cover

        pdb = Pdb()  # pragma: no cover
    except ImportError:
        warnings.warn(
            UserWarning(
                "Python's built-in pdb was selected as a debugger. "
                "If you want to use IPython as a debugger you have to "
                "'pip install radish-bdd[ipython-debugger]'"
            )
        )
        import pdb

    return pdb


def get_func_pos_args_as_kwargs(func, pos_arg_values):
    """Get the positional function arguments as keyword arguments given their values"""
    pos_arg_names = func.__code__.co_varnames[
        1 : func.__code__.co_argcount
    ]  # without the `step` argument
    kwargs = dict(zip(pos_arg_names, pos_arg_values))
    return kwargs


def locate_python_object(name):
    """
    Locate the object for the given name
    """
    obj = pydoc.locate(name)
    if not obj:
        obj = globals().get(name, None)

    return obj


def yaml_ordered_load(
    stream, loader_type=yaml.SafeLoader, object_pairs_hook=OrderedDict
):
    """Load YAML using an OrderedDict

    This function is needed for reproducibility with Python 3.5,
    which doesn't guarantee dict key ordering.
    """

    class OrderedLoader(loader_type):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )

    return yaml.load(stream, OrderedLoader)
