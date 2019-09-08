"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from collections import defaultdict


class StepImpl:
    """Represents a Step Implementation registered at the ``StepRegistry``

    A Step Implementation represents a function which is mapped to
    a Step text when running a Feature File.
    """

    __slots__ = ["keyword", "pattern", "func"]

    def __init__(self, keyword, pattern, func):
        self.keyword = keyword
        self.pattern = pattern
        self.func = func

    def __repr__(self) -> str:
        return "<StepImpl for '{}' with keyword '{}'>".format(
            self.pattern, self.keyword
        )  # pragma: no cover

    def __hash__(self):
        return hash((self.keyword, self.pattern, self.func))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return (
            self.keyword == other.keyword
            and self.pattern == other.pattern  # noqa
            and self.func == other.func  # noqa
        )


class StepRegistry:
    """The ``StepRegistry`` keeps track of all declared ``StepImpl``s.

    The registered ``StepImpl``s will be used by the ``Matcher`` to
    assign to ``Step`` for execution.
    """

    #: Holds a set of keywords which can be used to register a Step Implementation.
    #  The ``And`` and ``But`` gherkin keywords are not part of this set because
    #  those can be used in all of the contexts of the keywords below.
    #  The ``Step`` keyword is used to register Step Implementations which are
    #  applicable for all the others.
    KEYWORDS = {"Given", "When", "Then", "Step"}

    def __init__(self):
        self._step_implementations = defaultdict(list)

    def step_implementations(self, keyword=None):
        """Return a dict of all registered Step Implementations"""
        if keyword is not None:
            return (
                self._step_implementations[keyword] + self._step_implementations["Step"]
            )

        return self._step_implementations

    def register(self, keyword, pattern, func):
        """Register the given ``pattern`` with the given ``func`` as Step Implementation"""
        step_impl = StepImpl(keyword, pattern, func)
        if step_impl in self._step_implementations[keyword]:
            # NOTE: allow a Step Implementation to be registered multiple times.
            #       This can happend when one step module imports another in the same
            #       RADISH_BASEDIR.
            return

        self._step_implementations[keyword].append(step_impl)

    def create_step_decorators(self, context=None):
        """Create Step decorators for all ``KEYWORDS`` and the generic ``step`` decorator.

        The created Step decorators are injected into the given ``dict``-like ``context`` object.
        If the given ``context`` is ``None`` the Steps will be injected into ``globals()``.
        """
        if context is None:
            context = globals()

        created_decorator_names = []
        for keyword in self.KEYWORDS:

            def __create_decorator(keyword):
                def __decorator(pattern):
                    def __wrapper(func):
                        self.register(keyword, pattern, func)
                        return func

                    return __wrapper

                __decorator.__doc__ = """Decorator to assign a {keyword} Step Text Pattern to a Python function

                This Python function will be run when ever a Step in the Feature File matches the
                Step Text Pattern.
                It only matches a pattern in the ``{keyword}`` context.

                For example the following Step Implementation ...

                .. code-block:: python

                    @{keyword_func}("a simple {keyword_func} Step")
                    def some_step_implementation(step):
                        assert True, "Step failed to run"

                ... will match the following Steps in our Feature File:

                .. code-block:: gherkin

                    {keyword} a simple given Step
                    And a simple given Step

                ... but it will not match Steps using any other keywords.
                """.format(
                    keyword=keyword, keyword_func=keyword.lower()
                )

                return __decorator

            decorator_name = keyword.lower()
            context[decorator_name] = __create_decorator(keyword)
            created_decorator_names.append(decorator_name)
        return created_decorator_names


#: Holds a global instance of the StepRegistry which shall be used
#  by all modules implementing Steps.
registry = StepRegistry()
__all__ = registry.create_step_decorators()
