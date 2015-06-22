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
        s = Scenario(1, "Scenario", "Some scenario", None, None, None, [Scenario.Tag("foo", None), Scenario.Tag("bar", None), Scenario.Tag("bad_case", None)])
        s.absolute_id = 1
        s.has_to_run.when.called_with(None, None, ["foo"]).should.return_value(True)
        s.has_to_run.when.called_with(None, None, ["good_case", "foo"]).should.return_value(True)
        s.has_to_run.when.called_with(None, None, ["good_case", "bar", "bad_case"]).should.return_value(True)
        s.has_to_run.when.called_with(None, None, ["good_case"]).should.return_value(False)

        s.has_to_run.when.called_with([1], None, None).should.return_value(True)
        s.has_to_run.when.called_with([1, 2], None, None).should.return_value(True)
        s.has_to_run.when.called_with([2], None, None).should.return_value(False)

        s.has_to_run.when.called_with([1], None, ["good_case"]).should.return_value(True)
        s.has_to_run.when.called_with([1, 2], None, ["foo", "bad_case"]).should.return_value(True)
        s.has_to_run.when.called_with([5, 4], None, ["bad_case"]).should.return_value(True)
        s.has_to_run.when.called_with([6], None, ["good_case"]).should.return_value(False)
