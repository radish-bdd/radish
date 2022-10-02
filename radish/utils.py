# -*- coding: utf-8 -*-

"""
This module provides several utility functions
"""

import os
import re
import sys
import fnmatch
import traceback
import warnings
import pydoc
import itertools
import calendar
from datetime import datetime, timedelta


class Failure(object):  # pylint: disable=too-few-public-methods
    """
        Represents the fail reason for a step
    """

    def __init__(self, exception):
        """
            Initalizes the Step failure with a given Exception

            :param Exception exception: the exception shrown in the step
        """
        self.exception = exception
        self.reason = str(exception)
        self.traceback = traceback.format_exc()
        self.name = exception.__class__.__name__
        traceback_info = traceback.extract_tb(sys.exc_info()[2])[-1]
        self.filename = traceback_info[0]
        self.line = int(traceback_info[1])


def console_write(text):
    """
        Writes the given text to the console

        :param str text: the text which is printed to the console
    """
    print(str(text))


def expandpath(path):
    """
        Expands a path

        :param string path: the path to expand
    """
    return os.path.expanduser(os.path.expandvars(path))


def recursive_glob(root, pattern):
    """
        Recursively search for files with given pattern inside a path

        :param str root: the root location to start search
        :param str pattern: to pattern to look for. It's matched against the filenames under `root`.

        :rtype: list
        :returns: A list of matching files
    """
    matches = []
    for root, dirnames, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches


def get_debugger():
    """
        Returns a debugger instance
    """
    try:
        from IPython.core.debugger import Pdb

        pdb = Pdb()
    except ImportError:
        try:
            from IPython.Debugger import Pdb
            from IPython.Shell import IPShell

            IPShell(argv=[""])
            pdb = Pdb()
        except ImportError:
            warnings.warn(
                'pdb was selected as a debugger. If you want to use ipython as a debugger you have to "pip install radish-bdd[ipython-debugger]"'
            )
            import pdb

    return pdb


def format_utc_to_local_tz(utc_dt, fmt="%Y-%m-%dT%H:%M:%S"):
    """
    Formats the given UTC datetime as a string converted to the local timezone.

    If the datetime is ``None``, it will return an empty string.

    Args:
        datetime (Datetime): the UTC based datetime object
        fmt (str): optional format for the string
    """
    if not utc_dt:
        return ""

    def utc_to_local(utc_dt):
        timestamp = calendar.timegm(utc_dt.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        assert utc_dt.resolution >= timedelta(microseconds=1)
        return local_dt.replace(microsecond=utc_dt.microsecond)

    return utc_to_local(utc_dt).strftime(fmt)


def make_unique_obj_list(somelist, attr):
    """
        Make list with objects unique
        according to an objects attribute.
    """
    tmp = {}
    for item in somelist:
        tmp[attr(item)] = item
    return tmp.values()


def get_func_code(func):
    """
        Get the code object for the given function.
    """
    if sys.version_info[0] == 3:
        return func.__code__
    else:
        return func.func_code


def get_func_arg_names(func):
    """
        Get the argument names of the given function.
    """
    return get_func_code(func).co_varnames


def get_func_location(func):
    """
        Get the location where the given function is implemented.
    """
    func_code = get_func_code(func)
    return "{0}:{1}".format(func_code.co_filename, func_code.co_firstlineno)


def str_lreplace(pattern, replacement, string, escape_pattern=False, flags=0):
    """
    Only replace the pattern with replacement
    if the string starts with the pattern.
    """
    if escape_pattern:
        pattern = re.escape(pattern)

    return re.sub(r"^{0}".format(pattern), replacement, string, flags=flags)


def locate(name):
    """
    Locate the object for the given name
    """
    obj = pydoc.locate(name)
    if not obj:
        obj = globals().get(name, None)

    return obj


def flattened_basedirs(basedirs):
    """
    Flatten a list of basedirs.

    Multiple basedirs can be specified within a
    single element split by a colon.
    """
    separator = ";" if os.name == "nt" else ":"
    return list(x for x in itertools.chain(*(x.split(separator) for x in basedirs)) if x)


def split_unescape(s, delim, escape='\\', unescape=True):
    """
    >>> split_unescape('foo|bar', '|')
    ['foo', 'bar']
    >>> split_unescape(r'foo\|bar', '|')
    ['foo|bar']
    >>> split_unescape(r'foo\\|bar', '|', unescape=True)
    [r'foo|', 'bar']
    >>> split_unescape(r'foo\\|bar', '|', unescape=False)
    [r'foo\\', 'bar']
    >>> split_unescape(r'foo\', '|', unescape=True)
    [r'foo\']
    """
    ret = []
    current = []
    itr = iter(s)
    for ch in itr:
        if ch == escape:
            try:
                # skip the next character; it has been escaped!
                if not unescape:
                    current.append(escape)
                current.append(next(itr))
            except StopIteration:
                if unescape:
                    current.append(escape)
        elif ch == delim:
            # split! (add current to the list and reset it)
            ret.append(''.join(current))
            current = []
        else:
            current.append(ch)
    ret.append(''.join(current))
    return ret
