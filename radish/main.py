# -*- coding: utf-8 -*-

import sys

from radish.parser import FeatureParser
from radish.loader import Loader


def main(args):
    """
        Main entry point for radish
    """
    featurefile = args[0]
    featureparser = FeatureParser(featurefile)
    featureparser.parse()

    # load user's custom python files
    loader = Loader(args[1])
    loader.load_all()


if __name__ == "__main__":
    main(sys.argv[1:])
