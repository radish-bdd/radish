"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import bisect


class HookImpl:
    """Represent a single Hook Implementation"""
    __slots__ = [
        "what", "when", "func", "on_tags", "order"
    ]

    def __init__(self, what, when, func, on_tags, order):
        self.what = what
        self.when = when
        self.func = func
        self.on_tags = on_tags
        self.order = order

    def __repr__(self) -> str:
        return "<HookImpl @{}.{} for tags {} with order {}>".format(
            self.when, self.what, self.on_tags, self.order
        )

    def __hash__(self):
        return hash((self.what, self.when, self.func, self.on_tags, self.order))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return (
            self.what == other.what
            and self.when == other.when  # noqa
            and self.func == other.func  # noqa
            and self.on_tags == other.on_tags  # noqa
            and self.order == other.order  # noqa
        )

    def __lt__(self, other):
        return self.order < other.order

    def __le__(self, other):
        return self.order <= other.order

    def __gt__(self, other):
        return self.order > other.order

    def __ge__(self, other):
        return self.order >= other.order


class HookRegistry:
    """The ``HookRegistry`` keeps track of all declared ``HookImpl``s.
    """
    DEFAULT_HOOK_ORDER = 100

    def __init__(self):
        #: Holds a set of all possible Hook combinations
        self._hooks = {
            "before": {
                "all": [],
                "each_feature": [],
                "each_rule": [],
                "each_scenario": [],
                "each_step": []
            },
            "after": {
                "all": [],
                "each_feature": [],
                "each_rule": [],
                "each_scenario": [],
                "each_step": []
            },
        }

    def step_implementations(self, keyword=None):
        """Return a dict of all registered Step Implementations"""
        if keyword is not None:
            return (
                self._step_implementations[keyword] + self._step_implementations["Step"]
            )

        return self._step_implementations

    def register(self, what, when, func, on_tags, order):
        """Register the given Hook for later execution"""
        hook_impl = HookImpl(what, when, func, on_tags, order)
        if hook_impl in self._hooks[when][what]:
            # NOTE: allow a Hook Implementation to be registered multiple times.
            #       This can happend when one hook module imports another in the same
            #       RADISH_BASEDIR.
            return

        # insert the HookImpl in the order given by ``order``.
        bisect.insort_right(self._hooks[when][what], hook_impl)

    def create_hook_decorators(self, context=None):
        """Create Hook decorators for all hook combinations

        The created Hook decorators are injected into the given ``dict``-like ``context`` object.
        If the given ``context`` is ``None`` the Hooks will be injected into ``globals()``.
        """
        if context is None:
            context = globals()

        created_decorator_names = []
        for when, whats in self._hooks.items():
            class HookProvider:
                def __init__(self, when):
                    self.when = when

            when_object = HookProvider(when)

            for what in whats.keys():
                def __create_decorator(what, when):
                    def __decorator(on_tags=None, order=self.DEFAULT_HOOK_ORDER):
                        def __wrapper(func):
                            self.register(what, when, func, on_tags, order)
                            return func
                        return __wrapper
                    return __decorator

                setattr(when_object, what, __create_decorator(what, when))

            context[when] = when_object
            created_decorator_names.append(when)
        return created_decorator_names

    def call(self, what, when, model, *args, **kwargs):
        """Calls a registered Hook"""
        if when == "before":
            hooks = self._hooks[when][what]
        else:
            hooks = reversed(self._hooks[when][what])

        for hook_impl in hooks:
            # TODO: check if Hook has to run according to tags

            # TODO: proper error handling
            hook_impl.func(model, *args, **kwargs)


#: Holds a global instance of the HookRegistry which shall be used
#  by all modules implementing Hooks.
registry = HookRegistry()
__all__ = registry.create_hook_decorators()
