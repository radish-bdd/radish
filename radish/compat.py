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


def u(text):  # pragma: no cover
    """
    Encode given text to unicode utf-8 in manner that works accross various
    python interpreters and version. Currently only support CPython 2 and 3.

    :param text: text to encode
    :type text: str,unicode
    """
    # look for unicode in the builtins which only exists in python 2
    if PY2 is True:
        return unicode(text, "utf-8")

    return text


# base classes for strings types in python2/python3
if PY2:
    string_types = basestring,
else:
    string_types = str,


# python2/python3 compatible method to identify iterable that are not strings
if PY2:   # pragma: no cover
    def is_nonstr_iter(v):
        return hasattr(v, '__iter__')
else:
    def is_nonstr_iter(v):
        if isinstance(v, str):
            return False
        return hasattr(v, '__iter__')

# python2/python3 compatible pathname2url import
if PY2:   # pragma: no cover
    from urllib import pathname2url
else:
    from urllib.request import pathname2url
