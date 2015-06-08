# -*- coding: utf-8 -*-

import os
import sys
from docopt import docopt
from time import time

from radish import __VERSION__
from radish.parser import FeatureParser
from radish.loader import Loader
from radish.matcher import Matcher
from radish.stepregistry import StepRegistry
from radish.hookregistry import HookRegistry
from radish.core import Runner
from radish.exceptions import FeatureFileNotFoundError
from radish.errororacle import error_oracle
from radish.terrain import world
import radish.utils as utils

# extensions
# FIXME: load dynamically
import radish.extensions.console_writer
import radish.extensions.time_recorder
import radish.extensions.failure_inspector
import radish.extensions.failure_debugger
import radish.extensions.bdd_xml_writer


def setup_config(arguments):
    """
        Parses the docopt arguments and creates a configuration object in terrain.world
    """
    world.config = lambda: None
    for key, value in arguments.items():
        config_key = key.replace("--", "").replace("-", "_").replace("<", "").replace(">", "")
        setattr(world.config, config_key, value)


@error_oracle
def main(args):
    """
Usage:
    radish <features>...
           [-b=<basedir> | --basedir=<basedir>]
           [--early-exit]
           [--debug-steps]
           [--debug-after-failure]
           [--inspect-after-failure]
           [--bdd-xml]
    radish (-h | --help)
    radish (-v | --version)

Arguments:
    features                             feature files to run

Options:
    -h --help                            show this screen
    -v --version                         show version
    --early-exit                         stop the run after the first failed step
    --debug-steps                        debugs each step
    --debug-after-failure                start python debugger after failure
    --inspect-after-failure              start python shell after failure
    --bdd-xml                            write BDD XML result file after run

    -b=<basedir> --basedir=<basedir>     set base dir from where the step.py and terrain.py will be loaded [default: $PWD/radish]

(C) Copyright 2013 by Timo Furrer <tuxtimo@gmail.com>
    """

    arguments = docopt("radish {}\n{}".format(__VERSION__, main.__doc__), version=__VERSION__)

    # store all arguments to configuration dict in terrain.world
    setup_config(arguments)

    feature_files = []
    for given_feature in world.config.features:
        if not os.path.exists(given_feature):
            raise FeatureFileNotFoundError(given_feature)

        if os.path.isdir(given_feature):
            feature_files.extend(utils.recursive_glob(given_feature, "*.feature"))
            continue

        feature_files.append(given_feature)

    features = []
    for featureid, featurefile in enumerate(feature_files):
        featureparser = FeatureParser(featurefile, featureid + 1)
        featureparser.parse()
        features.append(featureparser.feature)

    if not features:
        print("Error: no features given")
        return 1

    # load user's custom python files
    loader = Loader(world.config.basedir)
    loader.load_all()

    # match feature file steps with user's step definitions
    matcher = Matcher()
    matcher.merge_steps(features, StepRegistry().steps)

    # run parsed features
    runner = Runner(HookRegistry(), early_exit=world.config.early_exit)
    runner.start(features, marker=int(time()))


if __name__ == "__main__":
    main(sys.argv[1:])
