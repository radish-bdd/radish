"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from parse_type import TypeBuilder  # noqa

from radish.errors import RadishError


class ParseTypeRegistry:
    """The ``ParseTypeRegistry`` keeps track of all custom registered parse type extensions"""

    def __init__(self):
        self.types = {}

    def register(self, name, func, pattern=None):
        """Register a new parse type"""
        if name in self.types:
            raise RadishError(
                "Cannot register custom parse type with name {} because it already exists".format(
                    name
                )
            )

        if pattern is not None:
            func.pattern = pattern

        self.types[name] = func

    def create_decorator(self, context=None):
        """Create the custom_type decorator.

        The created decorator is injected into the given ``dict``-like ``context`` object.
        If the given ``context`` is ``None`` the Steps will be injected into ``globals()``.
        """
        if context is None:
            context = globals()

        def __create_decorator(decorator_name):
            def __decorator(name, pattern):
                def __wrapper(func):
                    self.register(name, func, pattern)
                    return func

                return __wrapper

            return __decorator

        decorator_name = "custom_type"
        context[decorator_name] = __create_decorator(decorator_name)
        return decorator_name


#: Holds a global instance of the ParseTypeRegistry which shall be used
#  by all modules implementing Custom Parse Types.
registry = ParseTypeRegistry()


def register_custom_type(**kwargs):
    """Register a custom type

    The arguments are expected to be in the form of: type-name=func.
    """
    for name, func in kwargs.items():
        registry.register(name, func)


__all__ = registry.create_decorator()
