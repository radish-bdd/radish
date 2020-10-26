"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import inspect
import bisect

import tagexpressions

from radish.errors import HookExecError


class HookImpl:
    """Represent a single Hook Implementation"""

    __slots__ = ["what", "when", "func", "on_tags", "order", "is_formatter", "always"]

    def __init__(
        self, what, when, func, on_tags, order, is_formatter=False, always=False
    ):
        self.what = what
        self.when = when
        self.func = func
        self.on_tags = on_tags
        self.order = order
        self.is_formatter = is_formatter
        self.always = always

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self) -> str:
        return "<HookImpl @{}.{} for tags {} with order {}>".format(
            self.when, self.what, self.on_tags, self.order
        )

    def __hash__(self):
        return hash(
            (
                self.what,
                self.when,
                self.func,
                self.on_tags,
                self.order,
                self.is_formatter,
                self.always,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return (
            self.what == other.what
            and self.when == other.when  # noqa
            and self.func == other.func  # noqa
            and self.on_tags == other.on_tags  # noqa
            and self.order == other.order  # noqa
            and self.is_formatter == other.is_formatter  # noqa
            and self.always == other.always  # noqa
        )

    def __lt__(self, other):
        return self.order < other.order

    def __le__(self, other):
        return self.order <= other.order

    def __gt__(self, other):
        return self.order > other.order

    def __ge__(self, other):
        return self.order >= other.order


class GeneratorHookImpl:
    """Specialized Hook Implementation for Generator Hooks

    A Generator Hook uses a yield statement to separate
    the `before` and `after` part of a Hook.
    """

    def __init__(self, func):
        self.func = func
        self.generator = None

    def __call__(self, *args, **kwargs):
        if self.generator is None:
            # hook is called the first time, thus we create it and
            # consume the `before` part of it
            self.generator = self.func(*args, **kwargs)
            return next(self.generator)
        else:
            # the hook is called the second time, thus we
            # consume the `after` part of it and expect it to be exhausted
            try:
                return next(self.generator)
            except StopIteration:
                pass  # raised when the generator is exhausted

            # reset the generator for the next "before" call.
            # NOTE(TF): this introduces the thread-unsafety,
            #           which is fine for the moment, I guess ...
            #           A better implementation might be to use
            #           a factory approach which would create
            #           unique hook instances for each occurance.
            self.generator = None

    def __name__(self):
        return self.func.name


class HookRegistry:
    """The ``HookRegistry`` keeps track of all declared ``HookImpl``s"""

    DEFAULT_HOOK_ORDER = 100

    GENERATOR_HOOK_NAMES = {
        "for_all",
        "each_feature",
        "each_rule",
        "each_scenario",
        "each_step",
    }

    def __init__(self):
        #: Holds a set of all possible Hook combinations
        self._hooks = {
            "before": {
                "all": [],
                "each_feature": [],
                "each_rule": [],
                "each_scenario": [],
                "each_step": [],
            },
            "after": {
                "all": [],
                "each_feature": [],
                "each_rule": [],
                "each_scenario": [],
                "each_step": [],
            },
        }

    def register(
        self, what, when, func, on_tags, order, is_formatter=False, always=False
    ):
        """Register the given Hook for later execution"""
        if inspect.isgeneratorfunction(func):
            # the registered function is a generator hook
            generator_hook = GeneratorHookImpl(func)
            before_hook_impl = HookImpl(
                what, "before", generator_hook, on_tags, order, is_formatter, always
            )
            after_hook_impl = HookImpl(
                what, "after", generator_hook, on_tags, order * -1, is_formatter, always
            )

            if (
                before_hook_impl in self._hooks["before"][what]
                and after_hook_impl in self._hooks["after"][what]
            ):
                # NOTE: allow a Hook Implementation to be registered multiple times.
                #       This can happend when one hook module imports another in the same
                #       RADISH_BASEDIR.
                return

            # insert the HookImpl in the order given by ``order``.
            bisect.insort_right(self._hooks["before"][what], before_hook_impl)
            bisect.insort_right(self._hooks["after"][what], after_hook_impl)
        else:
            # we have regular hook
            hook_impl = HookImpl(what, when, func, on_tags, order, is_formatter, always)

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
                """whuat"""

                def __init__(self, when):
                    self.when = when

            when_object = HookProvider(when)

            for what in whats.keys():

                def __create_decorator(what, when):
                    def __decorator(
                        on_tags=None,
                        order=self.DEFAULT_HOOK_ORDER,
                        is_formatter=False,
                        always=False,
                    ):
                        if on_tags is None:
                            on_tags = []

                        def __wrapper(func):
                            self.register(
                                what, when, func, on_tags, order, is_formatter, always
                            )
                            return func

                        return __wrapper

                    __decorator.__doc__ = """Decorator to register a hook function

                    A hook function registered with this decorator will be run {when} {what}.

                    Args:
                        on_tags (list): a list of :class:`Tag` names for which this hook will be run
                        order (int): a number which is used to order the registered hooks when running them
                        is_formatter (bool): flag to indicate that the hook is a formatter.
                                             Formatter hooks are run even if ``on_tags`` do not match
                        always (bool): flag to indicate that the hook should always be run.
                                       Only enable this ``True`` if the hook doesn't depend on the Feature File
                                       you will be running.
                    """.format(  # noqa
                        when=when, what=what
                    )

                    return __decorator

                setattr(when_object, what, __create_decorator(what, when))

            context[when] = when_object
            created_decorator_names.append(when)
        return created_decorator_names

    def create_generator_hook_decorators(self, context=None):
        """Create Generator Hook decorators for models

        The created Hook decorators are injected into the given ``dict``-like ``context`` object.
        If the given ``context`` is ``None`` the Hooks will be injected into ``globals()``.
        """
        if context is None:
            context = globals()

        created_decorator_names = []
        for what in self.GENERATOR_HOOK_NAMES:

            def __create_decorator(what):
                def __decorator(
                    on_tags=None,
                    order=self.DEFAULT_HOOK_ORDER,
                    is_formatter=False,
                    always=False,
                ):
                    if on_tags is None:
                        on_tags = []

                    def __wrapper(func):
                        self.register(
                            what, None, func, on_tags, order, is_formatter, always
                        )
                        return func

                    return __wrapper

                __decorator.__doc__ = """Decorator to register a generator hook function

                A generator hook function registered with this decorator will be run
                twice for {what}, once for the `before` part before the yield statement and once
                after the yield statement for the `after` part.

                .. code-block:: python

                   @{what}
                   def do_{what}(model):
                       # do some setup
                       setup()
                       yield
                       # do some teardown
                       teardown()

                Args:
                    on_tags (list): a list of :class:`Tag` names for which this hook will be run
                    order (int): a number which is used to order the registered hooks when running them
                    is_formatter (bool): flag to indicate that the hook is a formatter.
                                         Formatter hooks are run even if ``on_tags`` do not match
                    always (bool): flag to indicate that the hook should always be run.
                                   Only enable this ``True`` if the hook doesn't depend on the Feature File
                                   you will be running.
                """.format(  # noqa
                    what=what
                )

                return __decorator

            context[what] = __create_decorator(what)
            created_decorator_names.append(what)
        return created_decorator_names

    def call(self, what, when, only_formatters, tagged_model, *args, **kwargs):
        """Calls a registered Hook"""
        hooks = self._hooks[when][what]
        for hook_impl in hooks:
            if not hook_impl.always:
                if only_formatters and not hook_impl.is_formatter:
                    continue

            #: holds a flag whether or not the Hook actually has to be called
            #  which is depenend on the `on_tags` setting of the HookImpl.
            call_hook = True

            if hook_impl.on_tags:
                tag_expression = tagexpressions.parse(" or ".join(hook_impl.on_tags))
                # get the Tags for models which actually have Tags
                tags = (
                    tagged_model.get_all_tags()
                    if hasattr(tagged_model, "get_all_tags")
                    else []
                )
                call_hook = tag_expression.evaluate([t.name for t in tags])

            if not call_hook:
                continue

            try:
                hook_impl(tagged_model, *args, **kwargs)
            except Exception as exc:
                raise HookExecError(hook_impl, exc) from exc


#: Holds a global instance of the HookRegistry which shall be used
#  by all modules implementing Hooks.
registry = HookRegistry()
__all__ = (
    registry.create_hook_decorators() + registry.create_generator_hook_decorators()
)
