# -*- coding: utf-8 -*-

"""
    Providing radish core functionality.
"""

from threading import Lock

from radish.parser import FeatureParser


# FIXME: rename
class Core(object):
    """
        Provide some core functionalities like parsing and storing of the feature files
    """
    def __init__(self):
        self.features = []
        self._scenario_id_lock = Lock()
        self._scenario_id = 0

    @property
    def next_scenario_id(self):
        """
            Returns the next scenario id
        """
        with self._scenario_id_lock:
            self._scenario_id += 1
            return self._scenario_id

    def parse_features(self, feature_files):
        """
            Parses the given feature files
        """
        for featurefile in feature_files:
            self.parse_feature(featurefile)

    def parse_feature(self, featurefile):
        """
            Parses the given feature file
        """
        featureparser = FeatureParser(self, featurefile, len(self.features) + 1)
        featureparser.parse()
        self.features.append(featureparser.feature)
