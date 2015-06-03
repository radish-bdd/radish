# -*- coding: utf-8 -*-

"""
    This module provides several utility functions
"""

import os


def expandpath(path):
    """
        Expands a path

        :param string path: the path to expand
    """
    return os.path.expanduser(os.path.expandvars(path))


def dirname(path):
    """
        Returns the dirname of the given path

        :param string path: the path to get the dirname
    """
    return os.path.dirname(expandpath(path))
