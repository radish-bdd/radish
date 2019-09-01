"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.terrain import world
from radish.config import Config


@pytest.fixture(name="default_config", scope="function")
def setup_default_config():
    """Setup a default radish config

    This config can be used by a components under test for most Test Cases.
    """
    return Config(
        {
            "wip_mode": False,
            "dry_run_mode": False,
            "debug_steps_mode": False,
            "tags": None,
            "tag_expression": None,
            "scenario_ids": [],
            "early_exit": False,
            "shuffle_scenarios": False,
            "no_ansi": False,
        }
    )


@pytest.fixture(name="world_default_config", scope="function")
def setup_world_default_config(default_config):
    """Setup a default radish config in the terrain world object"""
    if hasattr(world, "config"):
        orig_config = world.config
    else:
        orig_config = None

    world.config = default_config
    yield world.config

    if orig_config is not None:
        world.config = orig_config
    else:
        delattr(world, "config")
