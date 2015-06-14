# -*- coding: utf-8 -*-

from tests.base import *

from radish.scenario import Scenario


class ScenarioTestCase(RadishTestCase):
    """
        Tests for the scenario model class
    """
    def test_feature_has_to_run(self):
        """
            Test scenario's has to run functionality
        """
        s = Scenario(1, 1, "Scenario", "Some scenario", None, None, None, ["foo", "bar", "bad_case"])
        s.has_to_run.when.called_with(None, ["foo"]).should.return_value(True)
        s.has_to_run.when.called_with(None, ["good_case", "foo"]).should.return_value(True)
        s.has_to_run.when.called_with(None, ["good_case", "bar", "bad_case"]).should.return_value(True)
        s.has_to_run.when.called_with(None, ["good_case"]).should.return_value(False)

        s.has_to_run.when.called_with([1], None).should.return_value(True)
        s.has_to_run.when.called_with([1, 2], None).should.return_value(True)
        s.has_to_run.when.called_with([2], None).should.return_value(False)

        s.has_to_run.when.called_with([1], ["good_case"]).should.return_value(True)
        s.has_to_run.when.called_with([1, 2], ["foo", "bad_case"]).should.return_value(True)
        s.has_to_run.when.called_with([5, 4], ["bad_case"]).should.return_value(True)
        s.has_to_run.when.called_with([6], ["good_case"]).should.return_value(False)
