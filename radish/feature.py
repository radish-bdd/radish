# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Feature from a parsed feature file.
"""


class Feature(object):
    """
        Represent a Feature
    """

    def __init__(self, sentence, path, line):
        self.sentence = sentence
        self.path = path
        self.line = line
        self.description = []
        self.scenarios = []

    def __str__(self):
        return "Feature: {} from {}:{}".format(self.sentence, self.path, self.line)

    def __repr__(self):
        return "<Feature: {} from {}:{}>".format(self.sentence, self.path, self.line)
