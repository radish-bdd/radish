# -*- coding: utf-8 -*-

import sys

from radish.parser import FeatureParser


def main(args):
    """
        Main entry point for radish
    """
    featurefile = args[0]
    featureparser = FeatureParser(featurefile)


if __name__ == "__main__":
    main(sys.argv[1:])
