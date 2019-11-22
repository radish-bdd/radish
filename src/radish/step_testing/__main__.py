"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from pathlib import Path

import click
import colorful as cf

import radish.loader as loader
from radish.__main__ import expand_basedirs
from radish.config import Config
from radish.logger import enable_radish_debug_mode_click_hook, logger
from radish.stepregistry import registry as step_registry

from radish.step_testing.matcher import run_matcher_tests


def expand_matcher_configs(ctx, param, matcher_configs):
    """Expand the given matcher configuration files

    Expanding directories recursively for YAML files.
    """
    expanded_matcher_configs = []
    for matcher_config_file_location in (Path(f) for f in matcher_configs):
        if matcher_config_file_location.is_dir():
            expanded_matcher_configs.extend(
                list(matcher_config_file_location.glob("**/*.yml"))
            )
        else:
            expanded_matcher_configs.append(matcher_config_file_location)

    return expanded_matcher_configs


@click.command()
@click.version_option()
@click.help_option("--help", "-h")
@click.option(
    "--debug",
    "-d",
    "enable_debug_mode",
    is_flag=True,
    help="Enable debug mode for radish-test itself",
    callback=enable_radish_debug_mode_click_hook,
)
@click.option(
    "--basedir",
    "-b",
    "basedirs",
    multiple=True,
    default=("radish",),
    type=str,
    callback=expand_basedirs,
    help=(
        "Specify the location of the Step Implementations. "
        "One '-b' can contain multiple locations, split by a colon (:) [UNIX] "
        "or semicolon (;) [Windows]"
    ),
)
@click.option(
    "--no-ansi",
    "no_ansi",
    is_flag=True,
    help=("Turn off all ANSI sequences (colors, line rewrites)."),
)
@click.argument(
    "matcher-configs",
    nargs=-1,
    type=click.Path(exists=True),
    callback=expand_matcher_configs,
)
def cli(**kwargs):
    """radish - The root from red to green. BDD tooling for Python.

    radish-test can be used to perform tests for the Steps
    implemented in a radish base directory.

    Use the `MATCHER_CONFIGS` to pass configuration
    files containing the Step matchers.
    """
    config = Config(kwargs)

    # turn of ANSI colors if requested
    if config.no_ansi:
        cf.disable()

    logger.debug("Basedirs: %s", ", ".join(str(d) for d in config.basedirs))
    logger.debug("Loading all modules from the basedirs")
    loaded_modules = loader.load_modules(config.basedirs)
    logger.debug(
        "Loaded %d modules from the basedirs: %s",
        len(loaded_modules),
        ", ".join(str(m) for m in loaded_modules),
    )

    logger.debug(
        "Matcher configs: %s", ", ".join(str(m) for m in config.matcher_configs)
    )
    run_matcher_tests(config.matcher_configs, step_registry)


if __name__ == "__main__":
    cli()
