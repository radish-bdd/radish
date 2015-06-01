# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Step
"""


class Step(object):
    """
        Represents a step
    """

    def __init__(self, sentence, path, line):
        self.sentence = sentence
        self.path = path
        self.line = line
