# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Scenario
"""


class Scenario(object):
    """
        Represents a Scenario
    """

    def __init__(self, sentence, path, line):
        self.sentence = sentence
        self.path = path
        self.line = line
        self.steps = []
