# -*- coding: utf-8 -*-

from .terrain import world


__DOCS__ = "https://github.com/radish-bdd/radish"


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
        super(LanguageNotSupportedError, self).__init__("Language {0} could not be found".format(language))


class FeatureFileNotFoundError(RadishError):
    """
        Raised if a given feature file does not exist
    """
    def __init__(self, featurefile):
        self.featurefile = featurefile
        super(FeatureFileNotFoundError, self).__init__("Feature file '{0}': No such file".format(featurefile))


class FeatureFileSyntaxError(RadishError, SyntaxError):
    """
        If a a syntax error occured in a feature file
    """
    MESSAGE_TEMPLATE = """{msg}

Error Oracle says:
You have a SyntaxError in your feature file!
Please have a look into the radish documentation to found out which
features radish supports and how you could use them:
Link: {docs_link}"""

    def __init__(self, msg):
        super(FeatureFileSyntaxError, self).__init__(FeatureFileSyntaxError.MESSAGE_TEMPLATE.format(msg=msg, docs_link=__DOCS__))


class StepRegexError(RadishError, SyntaxError):
    """
        Raised if the step regex cannot be compiled.
    """
    def __init__(self, regex, step_func_name, re_error):
        self.regex = regex
        self.step_func_name = step_func_name
        self.re_error = re_error
        super(StepRegexError, self).__init__("Cannot compile regex '{0}' from step '{1}': {2}".format(regex, step_func_name, re_error))


class StepPatternError(RadishError, SyntaxError):
    """
        Raised if the steps pattern cannot be compiled.
    """
    def __init__(self, pattern, step_func_name, error):
        self.pattern = pattern
        self.step_func_name = step_func_name
        self.error = error
        super(StepPatternError, self).__init__("Cannot compile pattern '{0}' of step '{1}': {2}".format(pattern, step_func_name, error))


class SameStepError(RadishError):
    """
        Raised if two step regex are exactly the same.
    """
    MESSAGE_TEMPLATE = """Cannot register step {0} with regex '{1}' because it is already used by step {2}

Error Oracle says:
You have defined two step definitions with the same Regular Expression.
This is invalid since radish does not know which one is the one to go with.
If you have two similar step definition expressions but ones sentence is a subset of the other
you may want to add a $ to mark the sentence's end - take care of the code order - first comes first serves."""

    def __init__(self, regex, func1, func2):
        self.regex = regex
        self.func1 = func1
        self.func2 = func2
        super(SameStepError, self).__init__(SameStepError.MESSAGE_TEMPLATE.format(func2.__name__, regex, func1.__name__))


class StepDefinitionNotFoundError(RadishError):
    """
        Raised if the Matcher cannot find a step from the feature file in the registered steps.
    """
    MESSAGE_TEMPLATE = """Cannot find step definition for step '{sentence}' in {step_path}:{step_line}

Error Oracle says:
There is no step defintion for '{sentence}'.
All steps should be declared in a module located in {basedir}.
For example you could do:

@step(r"{sentence}")
def my_step(step):
    raise NotImplementedError("This step is not implemented yet")"""

    def __init__(self, step):
        self.step = step
        super(StepDefinitionNotFoundError, self).__init__(StepDefinitionNotFoundError.MESSAGE_TEMPLATE.format(
            sentence=step.sentence, step_path=step.path, step_line=step.line, basedir=' or '.join(world.config.basedir)))


class RunnerEarlyExit(RadishError):
    """
        Raised if the runner has to exit to run.
    """
    pass


class HookError(RadishError):
    """
        Raised if an exception was raised inside a hook
    """
    def __init__(self, hook_function, failure):
        self.hook_function = hook_function
        self.failure = failure
        super(HookError, self).__init__("Hook '{0}' from {1}:{2} raised: '{3}: {4}'".format(
            hook_function.__name__, hook_function.__code__.co_filename, hook_function.__code__.co_firstlineno, failure.name, failure.reason))


class ScenarioNotFoundError(RadishError):
    """
        Raised if a scenario cannot be found
    """
    def __init__(self, scenario_id, amount_of_scenarios):
        self.scenario_id = scenario_id
        self.amount_of_scenarios = amount_of_scenarios
        super(ScenarioNotFoundError, self).__init__("No scenario with id {0} found. Specify a scenario id between 1 and {1}".format(scenario_id, amount_of_scenarios))


class ValidationError(RadishError):
    """
        Raised by the user if a step is somehow not valid
    """
    pass
