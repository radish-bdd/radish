# -*- coding: utf-8 -*-

"""
    This module provides a registry for all hooks
"""

from singleton import singleton

from . import utils
from .exceptions import HookError

import tagexpressions


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
            def _decorator(self, *args, **kwargs):
                """
                    Actual hook decorator
                """
                if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
                    func = args[0]
                    # hook was called without argument -> legacy!
                    HookRegistry().register(self._when, what, func)  # pylint: disable=protected-access
                else:
                    # hook was called with argument
                    on_tags = kwargs.get('on_tags')

                    if on_tags:
                        expr = tagexpressions.parse(on_tags)
                        on_tags = lambda tags: expr.evaluate(tags)

                    def func(f):
                        HookRegistry().register(self._when, what, f, on_tags)
                        return f

                return func
            _decorator.__name__ = _decorator.fn_name = what
            setattr(cls, what, _decorator)

    def build_hooks(self):
        """
            Builds all hooks
        """
        for hook in self._hooks.keys():
            self.Hook.build_decorator(hook)

    def register(self, when, what, func, on_tags=None):
        """
            Registers a function as a hook
        """
        if on_tags is None:
            on_tags = lambda _: True  # if no tags are specified we always return True

        self._hooks[what][when].append((on_tags, func))

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

    def __has_to_run(self, model, on_tags):
        """
        Return if the given hook has to run or not
        depending on it's tags
        """
        if isinstance(model, list):
            return any(on_tags([t.name for t in m.all_tags]) for m in model)

        return on_tags([t.name for t in model.all_tags])


    def call(self, when, what, model, *args, **kwargs):
        """
            Calls a registered hook
        """
        for on_tags, func in self._hooks[what][when]:
            if not self.__has_to_run(model, on_tags):
                # # this hook does not have to run because
                # # it was excluded due to the tags for this model
                continue

            try:
                func(model, *args, **kwargs)
            except Exception as e:
                raise HookError(func, utils.Failure(e))
        return None

HookRegistry()
before = HookRegistry.Hook("before")  # pylint: disable=invalid-name
after = HookRegistry.Hook("after")  # pylint: disable=invalid-name
