"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import logging
from pathlib import Path

import click

from radish.parser import FeatureFileParser
from radish.runner import Runner
from radish.hookregistry import registry as hook_registry

# TODO: dynamically import
import radish.formatters.gherkin

logger = logging.getLogger("radish")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s [%(levelname)s]: %(message)s"
)


def enable_radish_debug_mode(ctx, param, enabled):
    """Enable radish for debugging"""
    if enabled:
        logger.setLevel(logging.DEBUG)
        logger.debug("Enabled debug mode")
    else:
        logger.setLevel(logging.ERROR)


@click.command()
@click.option(
    "--basedir", "-b", "basedirs",
    multiple=True, default=("radish",), type=click.Path(exists=True),
    help="Specify the location of the Step Implementations"
)
@click.option(
    "--debug", "-d", "enable_debug_mode", is_flag=True,
    help="Enable debug mode for radish itself",
    callback=enable_radish_debug_mode
)
@click.argument(
    "files", nargs=-1,
    type=click.Path(exists=True),
    callback=lambda _, __, x: [Path(p) for p in x])
def cli(files, basedirs, enable_debug_mode):
    """radish - The root from red to green. BDD tooling for Python.

    Use radish to run your Feature File.

    Provide the Feature files to run in FILES.
    """
    logger.debug("Feature Files: %s", ", ".join(str(p) for p in files))
    logger.debug("Basedirs: %s", ", ".join(str(d) for d in basedirs))

    parser = FeatureFileParser()

    features = []
    for feature_file in files:
        logger.debug("Parsing Feature File %s", feature_file)
        feature_ast = parser.parse_file(feature_file)
        features.append(feature_ast)

    # TODO: load basedir modules

    runner = Runner(hook_registry=hook_registry)
    logger.debug("Starting Runner")
    runner.start(features)


if __name__ == "__main__":
    cli()
