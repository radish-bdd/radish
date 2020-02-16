"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import textwrap

from radish.terrain import world


class RadishError(Exception):
    """Base-Exception for all radish based errors."""

    pass


class StepImplementationNotFoundError(RadishError):
    """Exception raised when no Step Implementation can be found for a Step"""

    def __init__(self, step):
        self.step = step

    def __str__(self) -> str:
        return textwrap.dedent(
            """
            Radish is unable to find a matching Step Implementation for the Step:
                "{keyword} {text}"

            This Step is defined in the Feature File {path} on Line {line}.
            You can register a Step Implementation by using the
            "{keyword_lower}" decorator and placing the code below in one of these modules:
            {basedirs}

            from radish import {keyword_lower}

            @{keyword_lower}("{text}")
            def my_awesome_step(step):
                raise NotImplementedError("Oups, no implementation for this Step, yet")
        """.format(
                keyword=self.step.keyword,
                keyword_lower=self.step.keyword.lower(),
                text=self.step.text,
                path=self.step.path,
                line=self.step.line,
                basedirs="\n".join(str(b) for b in world.config.basedirs),
            )
        )


class StepImplementationPatternNotSupported(RadishError):
    """
    Exception raised when a registered Step Implementation Pattern is not supported by any matcher
    """

    def __init__(self, step_impl):
        self.step_impl = step_impl


class StepBehaveLikeRecursionError(RadishError):
    """Exception raised when a recursion is detected in behave-like calls of a Step"""

    def __init__(self):
        super().__init__(
            "Detected a infinit recursion in your ``step.behave_like`` calls"
        )


class HookExecError(RadishError):
    """Exception raised when a Hook execution raised an Exception"""

    def __init__(self, hook_impl, orig_exc):
        self.hook_impl = hook_impl
        self.orig_exc = orig_exc
        super().__init__(
            "The '@{when}.{what}' Hook '{func_name}' raised an {exc_type}: {exc_msg}".format(
                when=hook_impl.when,
                what=hook_impl.what,
                func_name=hook_impl.func.__name__,
                exc_type=orig_exc.__class__.__name__,
                exc_msg=str(orig_exc),
            )
        )
