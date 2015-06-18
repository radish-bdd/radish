# -*- coding: utf-8 -*-

"""
    This module provides the Argument-Expression Registry
"""

import parse
from singleton import singleton


@singleton()
class ArgExpRegistry(object):
    """
        Registry for all custom argument expressions
    """
    def __init__(self):
        self._expressions = {}

    def register(self, name, func):
        """
            Registers a custom argument expression
        """
        # FIXME: check for duplications
        self._expressions[name] = func

    @property
    def expressions(self):
        """
            Returns all registered expressions
        """
        return self._expressions


class ArgumentExpression(object):  # pylint: disable=too-few-public-methods
    """
        Represents an object with the advanced regex parsing
    """
    def __init__(self, regex):
        self.regex = regex


def arg_expr(name, expression):
    """
        Decorator for custom argument expressions
    """
    def _decorator(func):
        """
            Actual decorator
        """
        func.pattern = expression
        ArgExpRegistry().register(name, func)

        def _wrapper(text):
            """
                Decorator wrapper
            """
            return func(text)
        return _wrapper
    return _decorator
