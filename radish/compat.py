"""
This module provide Python 3 compatability
"""

import sys

# RecursionError does not exist in Python < 3.5
RecursionError = RuntimeError if sys.version_info < (3, 5) else RecursionError
