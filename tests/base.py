# -*- coding: utf-8 -*-

import sure
from unittest import TestCase
from mock import Mock

from radish.stepregistry import StepRegistry


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
