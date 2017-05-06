# -*- coding: utf-8 -*-

"""
This module provides a script to test the
radish step implementations
"""

import sys

import colorful
from docopt import docopt

from radish import __VERSION__
from radish.testing.matches import test_step_matches_configs


# use only 8 ANSI colors
# FIXME(TF): change to true colors!
colorful.use_8_ansi_colors()


def main():
    """
Usage:
    radish-test matches <match-configs>...
        [-b=<basedir> | --basedir=<basedir>...]
        [--cover-min-percentage=<cover-min-percentage>]
        [--cover-show-missing]
    radish-test (-h | --help)
    radish-test (-v | --version)

Arguments:
    match-configs                                  configuration files of step matcher tests

Commands:
    matches                                        test if the step implementions actually match the expected sentences

Options:
    -h --help                                      show this screen
    -v --version                                   show version
    -b=<basedir> --basedir=<basedir>...            set base dir from where the step.py and terrain.py will be loaded. [default: $PWD/radish]
                                                   You can specify -b|--basedir multiple times. All files will be imported.
    --cover-min-percentage=<cover-min-percentage>  minimum percentage of step coverage for tests to pass
    --cover-show-missing                           show steps which are not tested

(C) Copyright by Timo Furrer <tuxtimo@gmail.com>
    """

    arguments = docopt("radish-test {0}\n{1}".format(__VERSION__, main.__doc__), version=__VERSION__)


    if arguments['matches']:
        return test_step_matches_configs(arguments['<match-configs>'],
             arguments['--basedir'], arguments['--cover-min-percentage'], arguments['--cover-show-missing'])


if __name__ == "__main__":
    sys.exit(main())
