# -*- coding: utf-8 -*-

"""
    Providing radish core functionality.
"""

from threading import Lock
from collections import OrderedDict

from .parser import FeatureParser


class Configuration(object):
    """
        Manage configuration. Attributes of the class are created from the
        names of the command line options and are set to the command line
        values.

        Attribute names are parsed from command-line options removing or
        replacing characters that can not be used in python variables.

        Specifically:
          * "-" is replaced with "_"
          * "--" is removed.
          * "<" and ">" are removed (they are used in positional arguments)

        :param arguments: command line arguments and their values
        :type arguments: dict-line object (i.e. docopt.Dict)
    """

    def __init__(self, arguments):
        for key, value in arguments.items():
            config_key = key.replace("--", "")\
                            .replace("-", "_")\
                            .replace("<", "")\
                            .replace(">", "")
            setattr(self, config_key, value)


# FIXME: rename
class Core(object):
    """
        Provide some core functionalities like parsing and storing of the feature files
    """
    def __init__(self):
        self.features = []
        self._features_to_run = OrderedDict()
        self._feature_id_lock = Lock()
        self._feature_id = 0
        self._scenario_id_lock = Lock()
        self._scenario_id = 0

    @property
    def features_to_run(self):
        """
            Return all parsed features which are to run
        """
        return [f for f in self._features_to_run.values()]

    @property
    def next_feature_id(self):
        """
            Returns the next feature id
        """
        with self._feature_id_lock:
            self._feature_id += 1
            return self._feature_id

    @property
    def next_scenario_id(self):
        """
            Returns the next scenario id
        """
        with self._scenario_id_lock:
            self._scenario_id += 1
            return self._scenario_id

    def parse_features(self, feature_files, tag_expr):
        """
            Parses the given feature files
        """
        for featurefile in feature_files:
            feature = self.parse_feature(featurefile, tag_expr, self.next_feature_id)

            if feature is not None:
                for scenario in feature.scenarios:
                    scenario.absolute_id = self.next_scenario_id

                self._features_to_run[featurefile] = feature

    def parse_feature(self, featurefile, tag_expr, featureid=0):
        """
            Parses the given feature file
            If the feature is alreay parsed then it will just return it

            :returns: the parsed feature
            :rtype: Feature
        """
        featureparser = FeatureParser(self, featurefile, featureid, tag_expr)
        feature = featureparser.parse()

        if feature is None:
            return None

        self.features.append(feature)
        return feature
