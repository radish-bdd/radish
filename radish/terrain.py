# -*- coding: utf-8 -*-

"""
    Terrain module providing step overlapping data containers
"""

import threading

from radish.hookregistry import before, after

world = threading.local()  # pylint: disable=invalid-name
