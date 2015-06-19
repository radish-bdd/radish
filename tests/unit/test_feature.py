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
        f = Feature(1, "Feature", "Some feature", None, None, [Feature.Tag("foo", None), Feature.Tag("bar", None), Feature.Tag("bad_case", None)])
        f.has_to_run.when.called_with(None, ["foo"], None).should.return_value(True)
        f.has_to_run.when.called_with(None, ["good_case", "foo"], None).should.return_value(True)
        f.has_to_run.when.called_with(None, ["good_case", "bar", "bad_case"], None).should.return_value(True)
        f.has_to_run.when.called_with(None, ["good_case"], None).should.return_value(False)

        f.scenarios.append(Mock(absolute_id=1, has_to_run=lambda x,y,z: False))
        f.scenarios.append(Mock(absolute_id=2, has_to_run=lambda x,y,z: False))
        f.scenarios.append(Mock(absolute_id=3, has_to_run=lambda x,y,z: False))

        f.has_to_run.when.called_with([1], None, None).should.return_value(True)
        f.has_to_run.when.called_with([1, 2], None, None).should.return_value(True)
        f.has_to_run.when.called_with([3], None, None).should.return_value(True)
        f.has_to_run.when.called_with([1, 4], None, None).should.return_value(True)
        f.has_to_run.when.called_with([5, 4], None, None).should.return_value(False)
        f.has_to_run.when.called_with([6], None, None).should.return_value(False)

        f.has_to_run.when.called_with([1], ["good_case"], None).should.return_value(True)
        f.has_to_run.when.called_with([1, 2], ["foo", "bad_case"], None).should.return_value(True)
        f.has_to_run.when.called_with([5, 4], ["bad_case"], None).should.return_value(True)
        f.has_to_run.when.called_with([6], ["good_case"], None).should.return_value(False)
