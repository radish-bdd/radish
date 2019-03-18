"""
This module provide Python 2 / Python 3 compatability
"""

import re

try:
    re_pattern = re.Pattern  # >= Python 3.7
except AttributeError:
    re_pattern = re._pattern_type
