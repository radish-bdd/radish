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
from radish.step import Step
import radish.utils as utils

# extensions
# FIXME: load dynamically
import radish.extensions.console_writer
import radish.extensions.time_recorder
import radish.extensions.failure_inspector
import radish.extensions.failure_debugger


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

    -b=<basedir> --basedir=<basedir>     set base dir from where the step.py and terrain.py will be loaded [default: $PWD/radish]

(C) Copyright 2013 by Timo Furrer <tuxtimo@gmail.com>
    """

    arguments = docopt("radish {}\n{}".format(__VERSION__, main.__doc__), version=__VERSION__)

    feature_files = []
    for given_feature in arguments["<features>"]:
        if not os.path.exists(given_feature):
            raise FeatureFileNotFoundError(given_feature)

        if os.path.isdir(given_feature):
            feature_files.extend(utils.recursive_glob(given_feature, "*.feature"))
            continue

        feature_files.append(given_feature)

    features = []
    for featureid, featurefile in enumerate(feature_files):
        featureparser = FeatureParser(featurefile, featureid)
        featureparser.parse()
        features.append(featureparser.feature)

    if not features:
        print("Error: no features given")
        return 1

    # configure step -> FIXME: maybe use config singleton?!
    Step.DEBUG = arguments["--debug-steps"]
    Step.USE_DEBUGGER = arguments["--debug-after-failure"]
    Step.USE_INSPECTOR = arguments["--inspect-after-failure"]

    # load user's custom python files
    loader = Loader(arguments["--basedir"])
    loader.load_all()

    # match feature file steps with user's step definitions
    matcher = Matcher()
    matcher.merge_steps(features, StepRegistry().steps)

    # run parsed features
    runner = Runner(HookRegistry(), early_exit=arguments["--early-exit"])
    runner.start(features, marker=int(time()))


if __name__ == "__main__":
    main(sys.argv[1:])
