# -*- coding: utf-8 -*-

"""
This module provides a script to test the
radish step implementations
"""

import sys

from docopt import docopt
from colorful import colorful

from radish import __VERSION__
from radish.testing.matches import test_step_matches


def main():
    """
Usage:
    radish-test matches [-b=<basedir> | --basedir=<basedir>]
    radish-test (-h | --help)
    radish-test (-v | --version)

Commands:
    matches                             test if the step implemention matchers actually match the expected sentences
                                        The match configuration can be found in radish-matches.yml

Options:
    -h --help                           show this screen
    -v --version                        show version
    -b=<basedir> --basedir=<basedir>    set base dir from where the step.py and terrain.py will be loaded [default: $PWD/radish]

(C) Copyright by Timo Furrer <tuxtimo@gmail.com>
    """

    arguments = docopt("radish-test {0}\n{1}".format(__VERSION__, main.__doc__), version=__VERSION__)


    if arguments['matches']:
        failed, passed = test_step_matches('tests/radish-matches.yml', arguments['--basedir'])
        report = colorful.bold_white('{0} sentences ('.format(failed + passed))
        if passed > 0:
            report += colorful.bold_green('{0} passed'.format(passed))

        if passed > 0 and failed > 0:
            report += colorful.bold_white(', ')

        if failed > 0:
            report += colorful.bold_red('{0} failed'.format(failed))
        report += colorful.bold_white(')')
        print('\n' + report)


if __name__ == "__main__":
    sys.exit(main())
