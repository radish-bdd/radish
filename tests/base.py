# -*- coding: utf-8 -*-

import sure
from unittest import TestCase
from mock import Mock, patch, MagicMock

from radish.stepregistry import StepRegistry
from radish.hookregistry import HookRegistry


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
