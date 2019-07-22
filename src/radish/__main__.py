"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import logging
import os
from pathlib import Path

import click

import radish.loader as loader
from radish.config import Config
from radish.extensionregistry import registry as extension_registry
from radish.hookregistry import registry as hook_registry
from radish.parser import FeatureFileParser
from radish.runner import Runner
from radish.stepregistry import registry as step_registry
from radish.terrain import world
from radish.errors import RadishError

# configure the radish command line logger which is used for debugging
logger = logging.getLogger("radish")
logging.basicConfig(
    level=logging.CRITICAL, format="%(asctime)s - %(name)s [%(levelname)s]: %(message)s"
)

# load radish built-in extensions
__SOURCE_DIR__ = Path(__file__).absolute().parent
__BUILT_IN_EXTENSIONS__ = [__SOURCE_DIR__ / "extensions", __SOURCE_DIR__ / "formatters"]
loaded_built_in_extensions = loader.load_modules(__BUILT_IN_EXTENSIONS__)


def enable_radish_debug_mode(ctx, param, enabled):
    """Enable radish for debugging"""
    if enabled:
        logger.setLevel(logging.DEBUG)
        logger.debug("Enabled debug mode")
    else:
        logger.setLevel(logging.ERROR)


def expand_basedirs(ctx, param, basedirs):
    """Expand the given basedirs setting

    A single basedirs can contain multiple basedir locations.
    The location must be split by a colon (:) on UNIX and
    with a semicolon (;) on Windows.
    """
    expanded_basedirs = []
    for unexpanded_basedirs in basedirs:
        separator = ";" if os.name == "nt" else ":"

        basedir_gen = (
            Path(os.path.expandvars(b)).expanduser()
            for b in unexpanded_basedirs.split(separator)
        )
        for basedir in basedir_gen:
            if not basedir.exists():
                raise OSError("The basedir '{}' does not exist.".format(basedir))

            expanded_basedirs.append(basedir)
    return expanded_basedirs


class CommandWithExtensionOptions(click.Command):
    """Click Command to extend the given Options with the radish extension options"""

    def __init__(self, *args, **kwargs):
        radish_params = kwargs.pop("params", [])
        extension_options = extension_registry.get_extension_options()
        super().__init__(*args, params=radish_params + extension_options, **kwargs)


@click.command(cls=CommandWithExtensionOptions)
@click.option(
    "--debug",
    "-d",
    "enable_debug_mode",
    is_flag=True,
    help="Enable debug mode for radish itself",
    callback=enable_radish_debug_mode,
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
    "--early-exit",
    "-e",
    "early_exit",
    is_flag=True,
    help="Aborts the Runner immediately when the first Scenario failed",
)
@click.option(
    "--tags",
    "tags",
    help="Filter for Features and Scenarios matching this Tag Expression"
)
@click.option(
    "--scenarios",
    "-s",
    "scenario_ids",
    default="",
    callback=lambda _, __, ids: [int(x.strip()) for x in ids.split(",") if x.strip()],
    help="Filter for Scenarios with it's Id in this comma-separated list"
)
@click.option(
    "--shuffle",
    "shuffle_scenarios",
    is_flag=True,
    help="Shuffle the running order for the Scenarios within a Feature"
)
@click.argument(
    "feature_files",
    nargs=-1,
    type=click.Path(exists=True),
    callback=lambda _, __, x: [Path(p) for p in x],
)
def cli(**kwargs):
    """radish - The root from red to green. BDD tooling for Python.

    Use radish to run your Feature File.

    Provide the Feature files to run in FEATURE_FILES.
    """
    config = Config(kwargs)
    world.config = config

    logger.debug(
        "Loaded %d built-in extension modules: %s",
        len(loaded_built_in_extensions),
        ", ".join(str(e) for e in loaded_built_in_extensions),
    )
    logger.debug("Feature Files: %s", ", ".join(str(p) for p in config.feature_files))
    logger.debug("Basedirs: %s", ", ".join(str(d) for d in config.basedirs))

    logger.debug("Loading extensions")
    loaded_extensions = extension_registry.load_extensions(config)
    logger.debug(
        "Loaded %d extensions: %s",
        len(loaded_extensions),
        ", ".join(type(e).__name__ for e in loaded_extensions),
    )

    parser = FeatureFileParser()

    features = []
    for feature_file in config.feature_files:
        logger.debug("Parsing Feature File %s", feature_file)
        feature_ast = parser.parse_file(feature_file)
        if feature_ast:
            features.append(feature_ast)

    logger.debug("Loading all modules from the basedirs")
    loaded_modules = loader.load_modules(config.basedirs)
    logger.debug(
        "Loaded %d modules from the basedirs: %s",
        len(loaded_modules),
        ", ".join(str(m) for m in loaded_modules),
    )

    try:
        runner = Runner(
            config, step_registry=step_registry, hook_registry=hook_registry
        )
        logger.debug("Starting Runner")
        runner.start(features)
        logger.debug("Finished Runner")
    except RadishError as exc:
        print("An error occured while running the Feature Files:", flush=True)
        print(exc)


if __name__ == "__main__":
    cli()
