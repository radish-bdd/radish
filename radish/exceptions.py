# -*- coding: utf-8 -*-


class RadishError(Exception):
    """
        General radish specific error
    """
    pass


class LanguageNotSupportedError(RadishError):
    """
        Raised if the language could not be found.
    """
    def __init__(self, language):
        self.language = language
        super(LanguageNotSupportedError, self).__init__("Language {} could not be found".format(language))
