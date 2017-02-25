# -*- coding: utf-8 -*-

import os
import sys
from time import time

from docopt import docopt
from colorful import colorful
import tagexpressions

from . import __VERSION__
from .core import Core
from .core import Configuration
from .loader import load_modules
from .matcher import merge_steps
from .stepregistry import StepRegistry
from .hookregistry import HookRegistry
from .runner import Runner
from .extensionregistry import ExtensionRegistry
from .exceptions import FeatureFileNotFoundError, ScenarioNotFoundError
from .errororacle import error_oracle, catch_unhandled_exception
from .terrain import world
from . import utils


def setup_config(arguments):
    """
        Parses the docopt arguments and creates a configuration object in terrain.world
    """
    world.config = Configuration(arguments)


def show_features(core):
    """
        Show the parsed features
    """
    # set needed configuration
    world.config.write_steps_once = True
    if not sys.stdout.isatty():
        world.config.no_ansi = True

    runner = Runner(HookRegistry(), show_only=True)
    runner.start(core.features_to_run, marker="show")
    return 0


def run_features(core):
    """
        Run the parsed features

        :param Core core: the radish core object
    """
    # set needed configuration
    world.config.expand = True

    # load user's custom python files
    load_modules(world.config.basedir)

    # match feature file steps with user's step definitions
    merge_steps(core.features, StepRegistry().steps)

    # run parsed features
    if world.config.marker == "time.time()":
        world.config.marker = int(time())

    # scenario choice
    amount_of_scenarios = sum(len(f.scenarios) for f in core.features_to_run)
    if world.config.scenarios:
        world.config.scenarios = [int(s) for s in world.config.scenarios.split(",")]
        for s in world.config.scenarios:
            if not 0 < s <= amount_of_scenarios:
                raise ScenarioNotFoundError(s, amount_of_scenarios)

    runner = Runner(HookRegistry(), early_exit=world.config.early_exit)
    return runner.start(core.features_to_run, marker=world.config.marker)


@error_oracle
def main():
    """
    Entrypont to radish.
    Setup up configuration, loads extensions, reads feature files and runs
    radish
    """

    # note: using doc string for usage, messes up Sphinx documantation
    usage = """
Usage:
    radish show <features>
           [--expand]
           [--no-ansi]
    radish <features>...
           [-b=<basedir> | --basedir=<basedir>]
           [-e | --early-exit]
           [--debug-steps]
           [-t | --with-traceback]
           [-m=<marker> | --marker=<marker>]
           [-p=<profile> | --profile=<profile>]
           [-d | --dry-run]
           [-s=<scenarios> | --scenarios=<scenarios>]
           [--shuffle]
           [--feature-tags=<feature_tags>]
           [--scenario-tags=<scenario_tags>]
           {0}
    radish (-h | --help)
    radish (-v | --version)

Arguments:
    features                                    feature files to run

Options:
    -h --help                                   show this screen
    -v --version                                show version
    -e --early-exit                             stop the run after the first failed step
    --debug-steps                               debugs each step
    -t --with-traceback                         show the Exception traceback when a step fails
    -m=<marker> --marker=<marker>               specify the marker for this run [default: time.time()]
    -p=<profile> --profile=<profile>            specify the profile which can be used in the step/hook implementation
    -b=<basedir> --basedir=<basedir>            set base dir from where the step.py and terrain.py will be loaded [default: $PWD/radish]
    -d --dry-run                                make dry run for the given feature files
    -s=<scenarios> --scenarios=<scenarios>      only run the specified scenarios (comma separated list)
    --shuffle                                   shuttle run order of features and scenarios
    --feature-tags=<feature_tags>               only run features with the given tags
    --scenario-tags=<scenario_tags>             only run scenarios with the given tags
    --expand                                    expand the feature file (all preconditions)
    {1}

(C) Copyright by Timo Furrer <tuxtimo@gmail.com>
    """

    # load extensions
    load_modules(os.path.join(os.path.dirname(__file__), "extensions"))

    extensions = ExtensionRegistry()
    # add arguments from extensions to the usage
    usage = usage.format(extensions.get_options(), extensions.get_option_description())

    sys.excepthook = catch_unhandled_exception

    # add version to the usage
    arguments = docopt("radish {0}\n{1}".format(__VERSION__, usage), version=__VERSION__)

    # store all arguments to configuration dict in terrain.world
    setup_config(arguments)

    # load needed extensions
    extensions.load(world.config)

    core = Core()

    feature_files = []
    for given_feature in world.config.features:
        if not os.path.exists(given_feature):
            raise FeatureFileNotFoundError(given_feature)

        if os.path.isdir(given_feature):
            feature_files.extend(utils.recursive_glob(given_feature, "*.feature"))
            continue

        feature_files.append(given_feature)

    # parse feature and scenario tag expressions
    feature_tag_expression = None
    if world.config.feature_tags:
        feature_tag_expression = tagexpressions.parse(world.config.feature_tags)

    scenario_tag_expression = None
    if world.config.scenario_tags:
        scenario_tag_expression = tagexpressions.parse(world.config.scenario_tags)
    core.parse_features(feature_files, feature_tag_expression, scenario_tag_expression)

    if not core.features or sum(len(f.scenarios) for f in core.features) == 0:
        print(colorful.bold_red('Error: ') + colorful.red('please specify at least one feature to run'))
        if feature_tag_expression or scenario_tag_expression:
            print(colorful.red('You have specified a feature or scenario expression. Make sure those are valid and actually yield some features to run.'))
        return 1

    argument_dispatcher = [
        ((lambda: world.config.show), show_features),
        ((lambda: True), run_features)
    ]

    # radish command dispatching
    for to_run, method in argument_dispatcher:
        if to_run():
            return method(core)


if __name__ == "__main__":
    sys.exit(main())
