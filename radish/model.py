# -*- coding: utf-8 -*-

"""
    This model provides a base class for all models:

    Models:
        * Feature
        * Scenario
        * ScenarioOutline
        * Step
"""


# FIXME: make ABC
class Model(object):
    """
        Represents a base model
    """
    def __init__(self, id, keyword, sentence, path, line, parent=None):
        self.id = id
        self.keyword = keyword
        self.sentence = sentence
        self.path = path
        self.line = line
        self.parent = parent
