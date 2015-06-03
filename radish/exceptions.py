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


class StepRegexError(RadishError, SyntaxError):
    """
        Raised if the step regex cannot be compiled.
    """
    def __init__(self, regex, step_func_name, re_error):
        self.regex = regex
        self.step_func_name = step_func_name
        self.re_error = re_error
        super(StepRegexError, self).__init__("Cannot compile regex '{}' from step '{}': {}".format(regex, step_func_name, re_error))


class SameStepError(RadishError):
    """
        Raised if two step regex are exactly the same.
    """
    def __init__(self, regex, func1, func2):
        self.regex = regex
        self.func1 = func1
        self.func2 = func2
        super(SameStepError, self).__init__("Cannot register step {} with regex '{}' because it is already used by step {}".format(func2.__name__, regex, func1.__name__))


class StepDefinitionNotFoundError(RadishError):
    """
        Raised if the Matcher cannot find a step from the feature file in the registered steps.
    """
    def __init__(self, step):
        self.step = step
        super(StepDefinitionNotFoundError, self).__init__("Cannot find step definition for step '{}' in {}:{}".format(step.sentence, step.path, step.line))
