# -*- coding: utf-8 -*-

"""
    This module provide Oython 2 / Python 3 compatability
"""

def unicode_(text):  # pragma: no cover
    """
    Encode given test to unicode utf-8 in manner that works accross python 2 and 3.

    :param text: text to encode
    :type text: str,unicode
    """
    # look for unicode in the builtins which only exists in python 2
    if hasattr(globals()['__builtins__'], 'unicode') is True:
        unicode_text = unicode(text, "utf-8")
    else:
        unicode_text = text

    return unicode_text

