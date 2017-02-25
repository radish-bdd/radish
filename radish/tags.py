"""
Module with functionality to work with tags.
"""


class Tag(object):
    """
    Represents a tag for a model
    """
    def __init__(self, name, arg=None):
        self.name = name
        self.arg = arg
