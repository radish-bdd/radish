# -*- coding: utf-8 -*-

import sys
from docopt import docopt

from radish import __VERSION__
from radish.parser import FeatureParser
from radish.loader import Loader
from radish.matcher import Matcher
from radish.stepregistry import StepRegistry
from radish.hookregistry import HookRegistry
from radish.core import Runner

# extensions
# FIXME: load dynamically
import radish.extensions.console_writer


def main(args):
    """
Usage:
    radish <features>...
           [-b=<basedir> | --basedir=<basedir>]
    radish (-h | --help)
    radish (-v | --version)

Arguments:
    features                             feature files to run

Options:
    -h --help                            show this screen
    -v --version                         show version

    -b=<basedir> --basedir=<basedir>     set base dir from where the step.py and terrain.py will be loaded [default: $PWD/radish]

(C) Copyright 2013 by Timo Furrer <tuxtimo@gmail.com>
    """

    arguments = docopt("radish {}\n{}".format(__VERSION__, main.__doc__), version=__VERSION__)

    features = []
    for featurefile in arguments["<features>"]:
        featureparser = FeatureParser(featurefile)
        featureparser.parse()
        features.append(featureparser.feature)

    if not features:
        print("Error: no features given")
        return 1

    # load user's custom python files
    loader = Loader(arguments["--basedir"])
    loader.load_all()

    matcher = Matcher()
    matcher.merge_steps(features, StepRegistry().steps)

    runner = Runner(features, HookRegistry())
    runner.start()


if __name__ == "__main__":
    main(sys.argv[1:])
