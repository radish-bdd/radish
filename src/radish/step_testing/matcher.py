"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from pathlib import Path
from typing import List, Dict, Any
from unittest import mock
from collections import OrderedDict, defaultdict
import textwrap

import colorful as cf

import radish.matcher as matcher
import radish.utils as utils
from radish.errors import RadishError, StepImplementationNotFoundError
from radish.models import Step
from radish.stepregistry import StepRegistry


def parse_matcher_config(matcher_config_path):
    """Parse the given matcher config file

    The matcher config file is expected to be a properly
    formatted YAML file, having the following structure:

    .. code-block:: yaml

        - step: <step text>
          should_match | should_not_match: <step implementation func name>
          with_arguments:
            - <args...>


    The YAML file can contain one or more of these ``step`` blocks.
    """
    with matcher_config_path.open("r", encoding="utf-8") as matcher_config_file:
        steps_matcher_config = utils.yaml_ordered_load(matcher_config_file)

    # the matcher config is empty - so we don't have to continue here
    if not steps_matcher_config:
        return None

    # validate the matcher config read from the YAML file
    for step_matcher_config in steps_matcher_config:
        # check if the config really has the `step` key
        if "step" not in step_matcher_config:
            raise RadishError("All Matcher Config must start with the 'step' key")

        # check if the config has either the `should_match` or `should_not_match` key
        if ("should_match" not in step_matcher_config) == (
            "should_not_match" not in step_matcher_config
        ):  # noqa
            raise RadishError(
                "Each Matcher Config must either contain a 'should_match' or 'should_not_match' key"
            )

        # check if the config has any invalid keys
        valid_keys = {"step", "should_match", "should_not_match", "with_arguments"}
        if not set(step_matcher_config.keys()).issubset(valid_keys):
            raise RadishError(
                "All Matcher Config only allow the keys: "
                "{}. The following are not allowed: {}.".format(
                    ", ".join(sorted(valid_keys)),
                    ", ".join(
                        sorted(set(step_matcher_config.keys()).difference(valid_keys))
                    ),
                )
            )

    return steps_matcher_config


def run_matcher_tests(
    matcher_configs: List[Path], coverage_config, step_registry: StepRegistry
):
    """Run the matcher config tests against all Steps in the Registry"""
    #: holds a set of all covered Step Implementations
    #  A Step Implementation only counts as covered if it
    #  was successfully tested against a positive (should_match) test.
    covered_step_impls = set()

    for matcher_config_path in matcher_configs:
        match_config = parse_matcher_config(matcher_config_path)

        # nothing to match against, because config was empty
        if not match_config:
            print(
                cf.orange(
                    "The matcher config {} was empty - Nothing to do :)".format(
                        matcher_config_path
                    )
                )
            )
            continue

        for step_to_match in match_config:
            # create a dummy Step object for the match config
            keyword, text = step_to_match["step"].split(maxsplit=1)
            step = Step(
                step_id=0,
                keyword=keyword,
                used_keyword=keyword,
                text=text,
                doc_string=None,
                data_table=None,
                path=None,
                line=None,
            )
            # provide a Mock Scenario to the Step which
            # is needed for some Step matching functionality.
            step.scenario = mock.MagicMock(name="Mocked Scenario")

            # verify the step matches accordingly to the expectations in the config
            if "should_match" in step_to_match:
                expected_step_func = step_to_match["should_match"]
                if "with_arguments" in step_to_match:
                    expected_step_arguments = step_to_match["with_arguments"]
                else:
                    expected_step_arguments = []  # no Step arguments to match against

                is_matched = assert_step_match(
                    step, expected_step_func, expected_step_arguments, step_registry
                )
                if is_matched:
                    covered_step_impls.add(step.step_impl)
            else:
                assert_step_not_match(
                    step, step_to_match["should_not_match"], step_registry
                )

    # do coverage analysis on the tested Step Implementation coverage
    coverage(covered_step_impls, step_registry, coverage_config)


def assert_step_match(
    step: Step,
    expected_step_func: str,
    expected_step_arguments: List[Dict[str, Any]],
    step_registry: StepRegistry,
):
    """Assert that the Step correctly matches in the Registry"""
    print(
        "{} STEP '{}' SHOULD MATCH {}".format(
            cf.orange(">>"),
            cf.deepSkyBlue3("{} {}".format(step.keyword, step.text)),
            cf.deepSkyBlue3(expected_step_func),
        ),
        end="    ",
        flush=True,
    )

    # match the step text from the config with one from the registry
    try:
        matcher.match_step(step, step_registry)
    except StepImplementationNotFoundError:
        print_failure(None, ["Expected Step Text didn't match any Step Implementation"])
        return False

    # check if Step matches the correct Step Implementation Function
    matched_step_func = step.step_impl.func
    if matched_step_func.__name__ != expected_step_func:
        print_failure(
            matched_step_func,
            [
                "Expected Step Text matched {} instead of {}".format(
                    matched_step_func.__name__, expected_step_func
                )
            ],
        )
        return False

    # check if the Step has a match with the correct arguments
    if expected_step_arguments:
        # merge the Step's keyword and positional arguments into one dict
        args, kwargs = step.step_impl_match.evaluate()
        actual_step_arguments = utils.get_func_pos_args_as_kwargs(
            matched_step_func, args
        )
        actual_step_arguments.update(kwargs)

        # turn the list of single-item-dicts to a multi-item dict
        # -> [{1: 2}, {3: 4}] --> {1: 2, 3: 4}
        # NOTE(TF) for Python 3.5 test reproducibility we need an OrderedDict -.^
        expected_step_arguments = OrderedDict(
            (
                argpair
                for argpairs in expected_step_arguments
                for argpair in argpairs.items()
            )
        )
        errors = assert_step_arguments(actual_step_arguments, expected_step_arguments)

        if errors:
            print_failure(matched_step_func, errors)
            return False

    print(cf.bold_forestGreen("✔"))
    return True


def assert_step_not_match(
    step: Step, expected_step_func: str, step_registry: StepRegistry
):
    """Assert that the Step doesn't match a Step Implementation from the Registry"""
    print(
        "{} STEP '{}' SHOULD NOT MATCH {}".format(
            cf.orange(">>"),
            cf.deepSkyBlue3("{} {}".format(step.keyword, step.text)),
            cf.deepSkyBlue3(expected_step_func if expected_step_func else "ANY"),
        ),
        end="    ",
        flush=True,
    )

    # match the step text from the config with one from the registry
    try:
        matcher.match_step(step, step_registry)
    except StepImplementationNotFoundError:
        print(cf.bold_forestGreen("✔"))
        return True

    matched_step_func = step.step_impl.func
    if matched_step_func.__name__ == expected_step_func:
        print_failure(
            matched_step_func,
            [
                "Expected Step Text matched {} but it shouldn't".format(
                    expected_step_func
                )
            ],
        )
        return False

    print(cf.bold_forestGreen("✔"))
    return True


def assert_step_arguments(actual_step_arguments, expected_step_arguments):
    """Test the matches between the actual Step arguments and the expected step arguments"""
    # collect all argument errors and return them all at once
    errors = []

    for arg_name, arg_value in expected_step_arguments.items():
        # if an expected Step argument isn't present in the actual Step arguments
        if arg_name not in actual_step_arguments:
            errors.append(
                'Expected argument "{0}" is not in matched arguments {1}'.format(
                    arg_name, sorted(set(actual_step_arguments.keys()))
                )
            )
            continue

        #: holds a flag to indicate that the types representation
        #  should be used for a match and not the actual object value.
        use_repr = False

        # check if argument value is a dict, if yes we'll do thorough comparison
        if isinstance(arg_value, dict) and "type" not in arg_value.keys():
            # in case the argument should be treated as an actual Python dict
            _type = "dict"
            value = arg_value
        elif isinstance(arg_value, dict):
            _type = arg_value["type"]
            value = arg_value["value"]
            # Use repr protocol to match argument values
            use_repr = "use_repr" in arg_value and arg_value["use_repr"]

            # check if value should be casted to the given type
            if "cast" in arg_value and arg_value["cast"] is True:
                obj_type = utils.locate_python_object(_type)
                if obj_type is None:
                    errors.append(
                        'Cannot cast to type "{0}" because it is unknown'.format(_type)
                    )
                    continue

                try:
                    value = obj_type(value)
                except Exception:
                    errors.append(
                        'Failed to cast "{0}" to given type "{1}"'.format(value, _type)
                    )
                    continue
        else:
            _type = type(arg_value).__name__
            value = arg_value

        if not use_repr and _type != type(value).__name__:
            errors.append(
                "Conflicting argument configuration: given value is actually of "
                'type "{0}" although it should match a value of type "{1}"'.format(
                    type(value).__name__, _type
                )
            )
            continue

        if type(actual_step_arguments[arg_name]).__name__ != _type:
            errors.append(
                'Expected argument "{0}" is of type "{2}" but should be "{1}"'.format(
                    arg_name, type(actual_step_arguments[arg_name]).__name__, _type
                )
            )
            continue

        matched = None
        if use_repr:
            matched = repr(actual_step_arguments[arg_name]) != value
        else:
            matched = actual_step_arguments[arg_name] != value

        if matched:
            errors.append(
                'Expected argument "{0}" with value "{1}" does not match value "{2}"'.format(
                    arg_name, value, actual_step_arguments[arg_name]
                )
            )
    return errors


def print_failure(matched_step_func, errors: List[str]):
    """Print a failure message for matching errors"""
    print(cf.bold_firebrick("✘"), end=" ", flush=True)

    if matched_step_func is not None:
        func_code = matched_step_func.__code__
        print(
            cf.firebrick(
                "(at {}:{})".format(func_code.co_filename, func_code.co_firstlineno)
            ),
            end="",
            flush=True,
        )

    print(flush=True)

    for error in errors:
        print(cf.firebrick("  - {}".format(error)), flush=True)


def coverage(covered_step_impls, step_registry, coverage_config):
    """Analyse the coverage of the registered Step Implementations"""
    # get all Step Implementations
    all_step_impls = {
        step_impl
        for step_impls in step_registry.step_implementations().values()
        for step_impl in step_impls
    }

    if coverage_config.show_missing or coverage_config.show_missing_templates:
        # get all Step Implementations not covered
        not_covered_step_impls = list(all_step_impls.difference(covered_step_impls))

        if not not_covered_step_impls:
            print("Everything is covered!")
            return

        # sort not covered steps according their line number
        not_covered_step_impls.sort(key=lambda x: x.func.__code__.co_firstlineno)

        # order missing Step Implementations by the module they are implemented in
        ordered_not_covered_step_impls = defaultdict(list)
        for not_covered_step_impl in not_covered_step_impls:
            step_module = not_covered_step_impl.func.__code__.co_filename
            ordered_not_covered_step_impls[step_module].append(not_covered_step_impl)

        # output not covered Step Implementations per module
        for module_path, step_impls in ordered_not_covered_step_impls.items():
            print("Missing from: {}".format(cf.bold(module_path)))
            for step_impl in step_impls:
                print(
                    "  - {}:{}".format(
                        step_impl.func.__name__, step_impl.func.__code__.co_firstlineno
                    )
                )

        if coverage_config.show_missing_templates:
            # output template YAML to test the not covered Step Implementations
            print()
            print(
                "Add the following to your matcher-config.yml "
                "to cover the missing Step Implementations:"
            )
            for step_impl in not_covered_step_impls:
                print(
                    textwrap.dedent(
                        """
                      {cf.gray}# testing Step Implementation at {path}:{lineno}{cf.reset}
                      {cf.forestGreen}-{cf.reset} {cf.bold_dodgerBlue}step{cf.reset}{cf.red}: {cf.italic_lightSkyBlue}"<insert sample Step Text here>"{cf.reset}
                        {cf.bold_dodgerBlue}should_match{cf.reset}{cf.red}:{cf.reset} {step_impl_func_name}
                    """.format(  # noqa
                            cf=cf,
                            path=step_impl.func.__code__.co_filename,
                            lineno=step_impl.func.__code__.co_firstlineno,
                            step_impl_func_name=step_impl.func.__name__,
                        )
                    ).rstrip()
                )

                # check if function has arguments which can be tested
                arg_names = step_impl.func.__code__.co_varnames[
                    1 : step_impl.func.__code__.co_argcount
                ]  # without the `step` argument
                if arg_names:
                    argument_match_lines = [
                        "    {cf.forestGreen}-{cf.reset} {cf.bold_dodgerBlue}{arg}{cf.reset}{cf.red}:{cf.reset} {cf.italic}<insert argument value here>{cf.reset}".format(  # noqa
                            cf=cf, arg=x
                        )
                        for x in arg_names
                    ]
                    print(
                        "  {cf.bold_dodgerBlue}with_arguments{cf.reset}{cf.red}:{cf.reset}".format(
                            cf=cf
                        )
                    )  # noqa
                    print("\n".join(argument_match_lines))
                print()
