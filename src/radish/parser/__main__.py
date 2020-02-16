"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import sys
from pathlib import Path

import click
import colorful as cf

from radish.config import Config
from radish.terrain import world
from radish.parser.core import FeatureFileParser
from radish.errors import RadishError
from radish.logger import enable_radish_debug_mode_click_hook, logger


def expand_feature_files(ctx, param, feature_files):
    """Expand the given feature files

    Expanding directories recursively for Feature Files
    """
    expanded_feature_files = []
    for feature_file_location in (Path(f) for f in feature_files):
        if feature_file_location.is_dir():
            expanded_feature_files.extend(
                list(feature_file_location.glob("**/*.feature"))
            )
        else:
            expanded_feature_files.append(feature_file_location)

    return expanded_feature_files


@click.command()
@click.version_option()
@click.help_option("--help", "-h")
@click.option(
    "--debug",
    "-d",
    "enable_debug_mode",
    is_flag=True,
    help="Enable debug mode for radish itself",
    callback=enable_radish_debug_mode_click_hook,
)
@click.option(
    "--no-ansi",
    "no_ansi",
    is_flag=True,
    help=(
        "Turn off all ANSI sequences (colors, line rewrites) ."
        "This option is mainly used by the formatters"
    ),
)
@click.option(
    "--resolve-preconditions",
    "resolve_preconditions",
    is_flag=True,
    help="Resolve @preconditions when parsing the Feature Files",
)
@click.argument(
    "feature_files",
    nargs=-1,
    type=click.Path(exists=True),
    callback=expand_feature_files,
)
def cli(**kwargs):
    """radish - The root from red to green. BDD tooling for Python.

    Parse and Pretty Print the raw radish AST for the given Feature Files

    Provide the Feature Files to run in FEATURE_FILES.
    """
    config = Config(kwargs)
    world.config = config

    # turn of ANSI colors if requested
    if config.no_ansi:
        cf.disable()

    parser = FeatureFileParser(
        ast_transformer=None, resolve_preconditions=config.resolve_preconditions
    )

    for feature_file in config.feature_files:
        logger.info("Parsing Feature File %s", feature_file)
        try:
            feature_ast = parser.parse(feature_file)
            if feature_ast:
                print(feature_ast.pretty())
        except RadishError as exc:
            print("", flush=True)
            print(
                "An error occured while parsing the Feature File {}:".format(
                    feature_file
                ),
                flush=True,
            )
            print(exc, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    cli()
