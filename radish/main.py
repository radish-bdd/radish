# -*- coding: utf-8 -*-

import os
import sys
from docopt import docopt
from time import time

from . import __VERSION__
from .core import Core
from .loader import load_modules
from .matcher import Matcher
from .stepregistry import StepRegistry
from .hookregistry import HookRegistry
from .runner import Runner
from .extensionregistry import ExtensionRegistry
from .exceptions import FeatureFileNotFoundError, ScenarioNotFoundError, FeatureTagNotFoundError, ScenarioTagNotFoundError
from .errororacle import error_oracle, catch_unhandled_exception
from .terrain import world
from . import utils


def setup_config(arguments):
    """
        Parses the docopt arguments and creates a configuration object in terrain.world
    """
    world.config = lambda: None
    for key, value in arguments.items():
        config_key = key.replace("--", "").replace("-", "_").replace("<", "").replace(">", "")
        setattr(world.config, config_key, value)


def show_features(core):
    """
        Show the parsed features
    """
    # set needed configuration
    world.config.write_steps_once = True
    if not sys.stdout.isatty():
        world.config.no_ansi = True

    runner = Runner(HookRegistry(), dry_run=True)
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
    Matcher.merge_steps(core.features, StepRegistry().steps)

    # run parsed features
    if world.config.marker == "time.time()":
        world.config.marker = int(time())

    # scenario choice
    amount_of_scenarios = sum(len(f.scenarios) for f in core.features_to_run)
    if world.config.scenarios:
        world.config.scenarios = [int(s) for s in world.config.scenarios.split(",")]
        for s in world.config.scenarios:
            if not (0 < s <= amount_of_scenarios):
                raise ScenarioNotFoundError(s, amount_of_scenarios)

    # tags
    if world.config.feature_tags:
        world.config.feature_tags = [t for t in world.config.feature_tags.split(",")]
        for tag in world.config.feature_tags:
            if not any(f for f in core.features if tag in [t.name for t in f.tags]):
                raise FeatureTagNotFoundError(tag)

    if world.config.scenario_tags:
        world.config.scenario_tags = [t for t in world.config.scenario_tags.split(",")]
        for tag in world.config.scenario_tags:
            if not any(s for f in core.features for s in f.scenarios if tag in [t.name for t in s.tags]):
                raise ScenarioTagNotFoundError(tag)

    runner = Runner(HookRegistry(), early_exit=world.config.early_exit)
    return runner.start(core.features_to_run, marker=world.config.marker)


@error_oracle
def main():
    """
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

(C) Copyright 2013 by Timo Furrer <tuxtimo@gmail.com>
    """
    # load extensions
    load_modules(os.path.join(os.path.dirname(__file__), "extensions"))

    extensions = ExtensionRegistry()
    main.__doc__ = main.__doc__.format(extensions.get_options(), extensions.get_option_description())

    sys.excepthook = catch_unhandled_exception

    arguments = docopt("radish {0}\n{1}".format(__VERSION__, main.__doc__), version=__VERSION__)

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

    core.parse_features(feature_files)

    if not core.features:
        print("Error: no features given")
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
