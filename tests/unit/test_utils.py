# -*- coding: utf-8 -*-

from tests.base import *

import os

import radish.utils as utils


class UtilsTestCase(RadishTestCase):
    """
        Tests for the utils module
    """
    def test_expandpath(self):
        """
            Test the expandpath utils method
        """
        os.environ["SOMEVAR"] = "foobar"
        utils.expandpath.when.called_with("/some/path/with/$SOMEVAR").should.return_value("/some/path/with/foobar")
