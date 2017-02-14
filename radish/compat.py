# -*- coding: utf-8 -*-

"""
    This module provide Oython 2 / Python 3 compatability
"""

from sys import version_info

from .exceptions import PythonCompatibilityError


# flags to indicate Python versions
PY2 = None
"""
Flag to indication CPython 2 compatibility, set to True when running CPython 2
False otherwise
"""

PY3 = None
"""
Flag to indication CPython 2 compatibility, set to True when running CPython 3
False otherwise
"""

# check major version if 2 then set PY2 to True
if version_info[0] == 2:  # pragma: no cover
    PY2 = True
# check major version if 3 then set PY3 to True
elif version_info[0] == 3:  # pragma: no cover
    PY3 = True
else:   # pragma: no cover
    PY2 = False
    PY3 = False


def u(text):  # pragma: no cover
    """
    Encode given text to unicode utf-8 in manner that works accross various
    python interpreters and version. Currently only support CPython 2 and 3.

    :param text: text to encode
    :type text: str,unicode

    :raises PythonCompatibilityError:
       if unicode support is not handled by interpreter/version
    """
    # look for unicode in the builtins which only exists in python 2
    if PY2 is True:
        unicode_text = unicode(text, "utf-8")
    elif PY3 is True:
        unicode_text = text
    else:
        msg = "unicode support unhandled for this Python interpreter/version"
        raise PythonCompatibilityError(msg)

    return unicode_text
