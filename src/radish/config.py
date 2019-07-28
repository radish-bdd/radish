"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from tagexpressions import parse

from radish.errors import RadishError


class Config:
    """Represents the configuration of a radish test run"""

    def __init__(self, command_line_config):
        for opt_key, opt_value in command_line_config.items():
            setattr(self, opt_key, opt_value)

        # make some configuration options easily accessible
        if hasattr(self, "tags") and self.tags:
            try:
                self.tag_expression = parse(self.tags)
            except Exception as exc:
                raise RadishError(
                    "The given Tag Expression '{}' has Syntax Errors. "
                    "Please consult https://github.com/timofurrer/tag-expressions "
                    "for detailed information about the Tag Expression Syntax".format(
                        self.tags
                    )
                ) from exc
        else:
            self.tag_expression = None
