"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import os
import sys
import time
from pathlib import Path
import traceback

import click
import colorful as cf

import radish.loader as loader
from radish.config import Config
from radish.errors import RadishError
from radish.extensionregistry import registry as extension_registry
from radish.hookregistry import registry as hook_registry
from radish.logger import enable_radish_debug_mode_click_hook, logger
from radish.parser import FeatureFileParser
from radish.runner import Runner
from radish.stepregistry import registry as step_registry
from radish.terrain import world

# NOTE(TF): somehow doctest with pytest imports this module multiple times ...
if "doctest" not in sys.modules:
    # load radish built-in extensions
    __SOURCE_DIR__ = Path(__file__).absolute().parent
    __BUILT_IN_EXTENSIONS__ = [
        __SOURCE_DIR__ / "extensions",
        __SOURCE_DIR__ / "formatters",
    ]
    loaded_built_in_extensions = loader.load_modules(__BUILT_IN_EXTENSIONS__)


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


def evaluate_user_data(ctx, param, userdata):
    """Evaluate the given user-defined data

    The user data can be in a ``key=value`` or just
    ``key`` format.
    """
    userdata_dict = {}
    for raw_data in userdata:
        key, *value = raw_data.split("=")
        userdata_dict[key] = "=".join(value) if value else True
    if userdata_dict:
        logger.debug("Evaluated user-defined data: %s", userdata_dict)
    return userdata_dict


class CommandWithExtensionOptions(click.Command):
    """Click Command to extend the given Options with the radish extension options"""

    def __init__(self, *args, **kwargs):
        radish_params = kwargs.pop("params", [])
        extension_options = extension_registry.get_extension_options()
        super().__init__(*args, params=radish_params + extension_options, **kwargs)


@click.command(cls=CommandWithExtensionOptions)
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
    help="Filter for Features and Scenarios matching this Tag Expression",
)
@click.option(
    "--scenarios",
    "-s",
    "scenario_ids",
    default="",
    callback=lambda _, __, ids: [int(x.strip()) for x in ids.split(",") if x.strip()],
    help="Filter for Scenarios with it's Id in this comma-separated list",
)
@click.option(
    "--shuffle",
    "shuffle_scenarios",
    is_flag=True,
    help="Shuffle the running order for the Scenarios within a Feature",
)
@click.option(
    "--wip",
    "wip_mode",
    is_flag=True,
    help=(
        "Run in WIP mode. In the WIP mode every Scenario has to fail."
        "It's best combined by marked WIP Scenarios with a '@wip'-Tag "
        "and use '--tags wip' in combination with the '--wip' flag"
    ),
)
@click.option(
    "--dry-run",
    "dry_run_mode",
    is_flag=True,
    help=(
        "Run in Dry Run mode. In the Dry Run mode Steps are matched with "
        "their implementation, but not run. "
        "Only formatter Hooks are called"
    ),
)
@click.option(
    "--debug-steps",
    "debug_steps_mode",
    is_flag=True,
    help=(
        "Run in Debug Steps mode. In the Debug Steps mode every Step is "
        "run in a Python debugger"
    ),
)
@click.option(
    "--user-data",
    "-u",
    multiple=True,
    callback=evaluate_user_data,
    help=(
        "Add arbitrary user-defined data to the 'radish.world' object. "
        "The data can be in a 'key=value' form or just a key"
    ),
)
@click.option(
    "--marker",
    "-m",
    "marker",
    default=str(int(time.time())),
    help=("Unique Marker for this Run. " "The Marker can be used in reports and logs"),
)
@click.option(
    "--formatter",
    "-f",
    "formatter",
    default="Gherkin",
    type=click.Choice(["Gherkin", "Dots"]),
    help="The formatter to use for this Run. ",
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
    "--with-traceback",
    "-t",
    "with_traceback",
    is_flag=True,
    help=(
        "Show the Traceback for failed Steps. "
        "This option is only used by the formatters"
    ),
)
@click.argument(
    "feature_files",
    nargs=-1,
    type=click.Path(exists=True),
    callback=expand_feature_files,
)
def cli(**kwargs):
    """radish - The root from red to green. BDD tooling for Python.

    Use radish to run your Feature File.

    Provide the Feature Files to run in FEATURE_FILES.
    """
    config = Config(kwargs)
    world.config = config

    # turn of ANSI colors if requested
    if config.no_ansi:
        cf.disable()

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
        try:
            feature_ast = parser.parse(feature_file)
            if feature_ast:
                features.append(feature_ast)
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

    logger.debug("Loading all modules from the basedirs")
    try:
        loaded_modules = loader.load_modules(config.basedirs)
    except Exception as exc:
        print("", flush=True)
        print("An error occured while loading modules from the basedirs:", flush=True)
        print(exc, flush=True)
        if config.with_traceback:
            print("", flush=True)
            traceback.print_exc()
        sys.exit(1)

    logger.debug(
        "Loaded %d modules from the basedirs: %s",
        len(loaded_modules),
        ", ".join(str(m) for m in loaded_modules),
    )

    exit_status = 0
    try:
        runner = Runner(
            config, step_registry=step_registry, hook_registry=hook_registry
        )
        logger.debug(
            "Starting Runner WIP mode: %r, Dry-Run mode: %r",
            config.wip_mode,
            config.dry_run_mode,
        )
        success = runner.start(features)
        logger.debug("Finished Runner with status %s", success)

        exit_status = 0 if success else 1
    except RadishError as exc:
        print("", flush=True)
        print("An error occured while running the Feature Files:", flush=True)
        print(exc, flush=True)
        if config.with_traceback:
            print("", flush=True)
            traceback.print_exc()
        exit_status = 1

    sys.exit(exit_status)


if __name__ == "__main__":
    cli()
