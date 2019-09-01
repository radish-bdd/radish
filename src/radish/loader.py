"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import importlib.util
from pathlib import Path
from typing import List

from radish.errors import RadishError


def load_modules(locations: List[Path]) -> List[Path]:
    """Load all Python modules in the given locations

    All given locations must already be expanded regarding
    * Environment Variables
    * User Home Directory
    """
    loaded_modules = []
    for location in locations:
        if not location.exists():
            raise RadishError(
                "Location '{0}' to load modules does not exist".format(location)
            )

        for module_path in location.glob("**/*.py"):
            load_module(module_path)
            loaded_modules.append(module_path)

    return loaded_modules


def load_module(path: Path) -> None:
    """Load the given module into the Python runtime"""
    module_name = path.stem
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        raise ImportError(
            "Unable to import module '{0}' from '{1}': {2}".format(
                module_name, path, exc
            )
        ) from exc
