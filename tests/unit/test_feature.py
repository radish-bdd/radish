# -*- coding: utf-8 -*-

from tests.base import *

from radish.feature import Feature


class FeatureTestCase(RadishTestCase):
    """
        Tests for the feature model class
    """
    def test_feature_has_to_run(self):
        """
            Test feature's has to run functionality
        """
        f = Feature(1, "Feature", "Some feature", None, None, ["foo", "bar", "bad_case"])
        f.has_to_run.when.called_with(None, ["foo"]).should.return_value(True)
        f.has_to_run.when.called_with(None, ["good_case", "foo"]).should.return_value(True)
        f.has_to_run.when.called_with(None, ["good_case", "bar", "bad_case"]).should.return_value(True)
        f.has_to_run.when.called_with(None, ["good_case"]).should.return_value(False)

        f.scenarios.append(Mock(absolute_id=1))
        f.scenarios.append(Mock(absolute_id=2))
        f.scenarios.append(Mock(absolute_id=3))

        f.has_to_run.when.called_with([1], None).should.return_value(True)
        f.has_to_run.when.called_with([1, 2], None).should.return_value(True)
        f.has_to_run.when.called_with([3], None).should.return_value(True)
        f.has_to_run.when.called_with([1, 4], None).should.return_value(True)
        f.has_to_run.when.called_with([5, 4], None).should.return_value(False)
        f.has_to_run.when.called_with([6], None).should.return_value(False)

        f.has_to_run.when.called_with([1], ["good_case"]).should.return_value(True)
        f.has_to_run.when.called_with([1, 2], ["foo", "bad_case"]).should.return_value(True)
        f.has_to_run.when.called_with([5, 4], ["bad_case"]).should.return_value(True)
        f.has_to_run.when.called_with([6], ["good_case"]).should.return_value(False)
