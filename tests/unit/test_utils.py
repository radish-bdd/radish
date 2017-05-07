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

    def test_str_lreplace(self):
        """
        Test str_lreplace function
        """
        s = 'And I have the number'
        utils.str_lreplace('And ', 'Given ', s).should.be.equal('Given I have the number')

        case_s = 'AnD I have the number'
        utils.str_lreplace('(?i)and ', 'Given ', case_s).should.be.equal('Given I have the number')

        s = 'I have And the number'
        utils.str_lreplace('And ', 'Given ', s).should.be.equal('I have And the number')

        s = 'AndI have the number'
        utils.str_lreplace('And ', 'Given ', s).should.be.equal('AndI have the number')
