"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import warnings


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
