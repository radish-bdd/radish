# -*- coding: utf-8 -*-

"""
    This module provides a registry for all hooks
"""

from singleton import singleton

from . import utils
from .exceptions import HookError


@singleton()
class HookRegistry(object):
    """
        Represents an object with all registered hooks
    """
    def __init__(self):
        self._hooks = {}
        self.reset()
        self.build_hooks()

    @property
    def hooks(self):
        """
            Returns all registered hooks
        """
        return self._hooks

    class Hook(object):
        """
            Represents a hook object

            This object is needed to provide decorators like:
            * @before.all
            * @before.each_feature
        """
        def __init__(self, when):
            self._when = when

        @classmethod
        def build_decorator(cls, what):
            """
                Builds the hook decorator
            """
            def _decorator(self, func):
                """
                    Actual hook decorator
                """
                HookRegistry().register(self._when, what, func)  # pylint: disable=protected-access
                return func
            _decorator.__name__ = _decorator.fn_name = what
            setattr(cls, what, _decorator)

    def build_hooks(self):
        """
            Builds all hooks
        """
        for hook in self._hooks.keys():
            self.Hook.build_decorator(hook)

    def register(self, when, what, func):
        """
            Registers a function as a hook
        """
        self._hooks[what][when].append(func)

    def reset(self):
        """
            Resets all registerd hooks
        """
        self._hooks = {
            "all": {"before": [], "after": []},
            "each_feature": {"before": [], "after": []},
            "each_scenario": {"before": [], "after": []},
            "each_step": {"before": [], "after": []},
        }

    def call(self, when, what, *args, **kwargs):
        """
            Calls a registered hook
        """
        for hook in self._hooks[what][when]:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                raise HookError(hook, utils.Failure(e))
        return None

HookRegistry()
before = HookRegistry.Hook("before")  # pylint: disable=invalid-name
after = HookRegistry.Hook("after")  # pylint: disable=invalid-name
