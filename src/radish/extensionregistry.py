"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class ExtensionRegistry:
    """The ``ExtensionRegistry`` can be used to register radish extensions

    Extensions are used to inject behavior into a radish run.
    Most common it's used for generic hooks and formatters.
    """

    def __init__(self):
        self.extensions = []

    def register(self, klass):
        """Register the extension class to the registry"""
        if klass not in self.extensions:
            self.extensions.append(klass)

    def load_extensions(self, config):
        """Load all extensions which are required by the user to load"""
        loaded_extensions = []
        for extension in self.extensions:
            load_func = getattr(extension, "load")
            loaded_extension = load_func(config)
            if loaded_extension:
                loaded_extensions.append(loaded_extension)
        return loaded_extensions

    def get_extension_options(self):
        """Return a list of all Options provided by the registered extensions"""
        options = []
        for extension in self.extensions:
            extension_options = getattr(extension, "OPTIONS", None)
            if extension_options:
                options.extend(extension_options)
        return options


def extension(klass):
    """
        Registers the class as a radish extension
    """
    registry.register(klass)
    return klass


#: Holds a global instance of the ExtensionRegistry which shall be used
#  by all modules implementing Extensions
registry = ExtensionRegistry()
