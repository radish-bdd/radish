"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import logging

# configure the radish command line logger which is used for debugging
logger = logging.getLogger("radish")
logging.basicConfig(
    level=logging.CRITICAL, format="%(asctime)s - %(name)s [%(levelname)s]: %(message)s"
)


def enable_radish_debug_mode_click_hook(ctx, param, enabled):
    """Enable radish for debugging"""
    if enabled:
        logger.setLevel(logging.DEBUG)
        logger.debug("Enabled debug mode")
    else:
        logger.setLevel(logging.ERROR)


__all__ = ["logger", "enable_radish_debug_mode_click_hook"]
