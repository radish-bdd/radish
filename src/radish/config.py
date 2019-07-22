"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class Config:
    """Represents the configuration of a radish test run"""
    def __init__(self, command_line_config):
        for opt_key, opt_value in command_line_config.items():
            setattr(self, opt_key, opt_value)
