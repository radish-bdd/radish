# -*- coding: utf-8 -*-

import os
import tempfile

from tests.base import *

import radish.testing.matches as matches


class MatchesTestCase(RadishTestCase):
    """
    Unit tests for testing.matches module.
    """
    def test_unreasonable_min_coverage(self):
        """
        Test unreasonable minimum test coverage
        """
        matches.test_step_matches_configs.when.called_with(None, None, 101).should.return_value(3)

    def test_no_steps_found(self):
        """
        Test if basedir does not contain any steps to test against
        """
        with patch('radish.testing.matches.load_modules'):
            matches.test_step_matches_configs.when.called_with(None, None).should.return_value(4)


    def test_empty_matches_config(self):
        """
        Test empty matches config file
        """
        # create temporary file
        fd, tmpfile = tempfile.mkstemp()
        os.close(fd)

        with patch('radish.testing.matches.load_modules'), patch('radish.testing.matches.StepRegistry.steps') as steps_mock:
            steps_mock.return_value = [1, 2]
            matches.test_step_matches_configs.when.called_with([tmpfile], None).should.return_value(5)

        # delete temporary file
        os.remove(tmpfile)
