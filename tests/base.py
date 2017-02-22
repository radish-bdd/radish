# -*- coding: utf-8 -*-

import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import sure
from unittest import TestCase
from mock import Mock, patch, MagicMock

from radish.stepregistry import StepRegistry
from radish.hookregistry import HookRegistry


def is_python3(minor=0):
    """
        Check if python is in version 3.
    """
    return sys.version_info >= (3, minor)


class RadishTestCase(TestCase):
    """
        Base class for all radish tests.
    """
    def setUp(self):
        """
            Setup test

            Initialize all singletons
        """
        StepRegistry()
        return True

    def tearDown(self):
        """
            Tear down the test

            Delete all singletons
        """
        StepRegistry().clear()
        HookRegistry().reset()
