# -*- coding: utf-8 -*-

"""
This module provide Python 3 compatability
"""

from __future__ import unicode_literals

import sys
import re

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


try:
    re_pattern = re.Pattern  # >= Python 3.7
except AttributeError:
    re_pattern = re._pattern_type


# RecursionError does not exist in Python < 3.5
RecursionError = RuntimeError if sys.version_info < (3, 5) else RecursionError
