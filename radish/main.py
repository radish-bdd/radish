# -*- coding: utf-8 -*-

import os
import sys
import warnings
from time import time

from docopt import docopt
import colorful
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

# use only 8 ANSI colors
# FIXME(TF): change to true colors!
colorful.use_8_ansi_colors()


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
    for basedir in utils.flattened_basedirs(world.config.basedir):
        load_modules(basedir)

    # match feature file steps with user's step definitions
    merge_steps(core.features, StepRegistry().steps)

    # run parsed features
    if world.config.marker == "time.time()":
        world.config.marker = int(time())

    # scenario choice
    amount_of_scenarios = sum(len(f.scenarios) for f in core.features_to_run)
    if world.config.scenarios:
        world.config.scenarios = [
            int(s.strip().replace("=", "")) for s in world.config.scenarios.split(",")
        ]
        for s in world.config.scenarios:
            if not 0 < s <= amount_of_scenarios:
                raise ScenarioNotFoundError(s, amount_of_scenarios)

    runner = Runner(HookRegistry(), early_exit=world.config.early_exit)
    return runner.start(core.features_to_run, marker=world.config.marker)


@error_oracle
def main(args=None):
    """
    Entrypont to radish.
    Setup up configuration, loads extensions, reads feature files and runs
    radish
    """

    if args is None:
        args = sys.argv[1:]

    # note: using doc string for usage, messes up Sphinx documantation
    usage = """
Usage:
    radish show <features>
           [--expand]
           [--no-ansi]
    radish <features>...
           [-b=<basedir> | --basedir=<basedir>...]
           [-e | --early-exit]
           [--debug-steps]
           [-t | --with-traceback]
           [-m=<marker> | --marker=<marker>]
           [-p=<profile> | --profile=<profile>]
           [-d | --dry-run]
           [-s=<scenarios> | --scenarios=<scenarios>]
           [--shuffle]
           [--tags=<tags>]
           [--wip]
           [-f=<formatter> | --formatter=<formatter>]
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
    -b=<basedir> --basedir=<basedir>...         set base dir from where the step.py and terrain.py will be loaded. [default: $PWD/radish]
                                                You can specify -b|--basedir multiple times or split multiple paths with a colon (:) similar to $PATH. All files will be imported.
    -d --dry-run                                make dry run for the given feature files
    -s=<scenarios> --scenarios=<scenarios>      only run the specified scenarios (comma separated list)
    --shuffle                                   shuttle run order of features and scenarios
    --tags=<feature_tags>                       only run Scenarios with the given tags
    --wip                                       expects all tests to fail instead of succeeding
    -f=<formatter> --formatter=<formatter>      the output formatter which should be used. [default: gherkin]
    --expand                                    expand the feature file (all preconditions)
    {1}

(C) Copyright by Timo Furrer <tuxtimo@gmail.com>
    """

    warnings.simplefilter("always", DeprecationWarning)

    # load extensions
    load_modules(os.path.join(os.path.dirname(__file__), "extensions"))

    extensions = ExtensionRegistry()
    # add arguments from extensions to the usage
    usage = usage.format(extensions.get_options(), extensions.get_option_description())

    sys.excepthook = catch_unhandled_exception

    # add version to the usage
    arguments = docopt(
        "radish {0}\n{1}".format(__VERSION__, usage), argv=args, version=__VERSION__
    )

    # store all arguments to configuration dict in terrain.world
    setup_config(arguments)

    # disable colors if necessary
    if world.config.no_ansi:
        colorful.disable()
    else:
        colorful.use_8_ansi_colors()

    # load needed extensions
    extensions.load(world.config)

    core = Core()

    if world.config.profile:
        msg = (
            "Command line argument -p/--profile will be removed in a future version.  Please "
            "use -u/--user-data instead."
        )
        warnings.warn(msg, DeprecationWarning, stacklevel=1)

    feature_files = []
    for given_feature in world.config.features:
        if not os.path.exists(given_feature):
            raise FeatureFileNotFoundError(given_feature)

        if os.path.isdir(given_feature):
            feature_files.extend(utils.recursive_glob(given_feature, "*.feature"))
            continue

        feature_files.append(given_feature)

    # parse tag expressions
    tag_expression = None
    if world.config.tags:
        tag_expression = tagexpressions.parse(world.config.tags)

    core.parse_features(feature_files, tag_expression)

    if not core.features or sum(len(f.scenarios) for f in core.features) == 0:
        utils.console_write(colorful.bold_red("Error: ")
            + colorful.red("No feature or no scenario specified in at least one of the given feature files")
        )
        if tag_expression:
            utils.console_write(colorful.red(
                    "You have specified a tag expression. Make sure those are valid and actually yield some Scenarios to run."
                )
            )
        return 1

    argument_dispatcher = [
        ((lambda: world.config.show), show_features),
        ((lambda: True), run_features),
    ]

    # radish command dispatching
    for to_run, method in argument_dispatcher:
        if to_run():
            return method(core)


if __name__ == "__main__":
    sys.exit(main())
