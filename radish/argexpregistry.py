# -*- coding: utf-8 -*-

"""
    This module provides the Argument-Expression Registry
"""

from singleton import singleton

from .exceptions import RadishError

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
        if name in self._expressions:
            raise RadishError("Cannot register argument expression with name {0} because it already exists".format(name))

        self._expressions[name] = func

    @property
    def expressions(self):
        """
            Returns all registered expressions
        """
        return self._expressions


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

        return func
    return _decorator
