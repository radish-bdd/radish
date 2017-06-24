# -*- coding: utf-8 -*-

"""
This module provide Python 2 / Python 3 compatability
"""

import sys

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


# flags to indicate Python versions
PY2 = sys.version_info[0] == 2

# RecursionError does not exist in Python < 3.5
RecursionError = RuntimeError if sys.version_info < (3, 5) else RecursionError


def u(text):  # pragma: no cover
    """
    Encode given text to unicode utf-8 in manner that works accross various
    python interpreters and version. Currently only support CPython 2 and 3.

    :param text: text to encode
    :type text: str,unicode
    """
    # look for unicode in the builtins which only exists in python 2
    if PY2 is True:
        return unicode(text)

    return str(text)
