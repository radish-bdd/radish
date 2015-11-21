# -*- coding: utf-8 -*-

"""
    Provide plugin interface for radish extensions
"""

from singleton import singleton


@singleton()
class ExtensionRegistry(object):
    """
        Registers all extensions
    """
    DEFAULT_LOAD_PRIORITY = 1000

    def __init__(self):
        self.extensions = []
        self.loaded_extensions = []

    def register(self, extension_class):
        """
            Registers the class as a radish extension
        """
        self.extensions.append(extension_class)

    def load(self, config):
        """
            Loads all needed extensions
        """
        for ext in sorted(self.extensions, key=lambda x: getattr(x, "LOAD_PRIORITY", self.DEFAULT_LOAD_PRIORITY)):
            try:
                if ext.LOAD_IF(config):
                    self.loaded_extensions.append(ext())
            except AttributeError:
                pass

    def get_options(self):
        """
            Returns all options registered by plugins
        """
        options = []
        for ext in self.extensions:
            try:
                options.extend(opt[0] for opt in ext.OPTIONS)
            except AttributeError:
                pass
        return "\n           ".join("[{0}]".format(x) for x in options)

    def get_option_description(self):
        """
            Returns all option descriptions registerd by plugins
        """
        options = []
        for ext in self.extensions:
            try:
                options.extend("{0} {1}".format(opt[0].ljust(43), opt[1]) for opt in ext.OPTIONS)
            except AttributeError:
                pass
        return "\n    ".join(options)


def extension(klass):
    """
        Registers the class as a radish extension
    """
    ExtensionRegistry().register(klass)
    return klass
