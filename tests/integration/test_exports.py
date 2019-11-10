"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


def test_correct_exports_on_package_level():
    # THEN, can import top-level exports
    from radish import (  # noqa
        # Step Decorators
        given,
        when,
        then,
        step,
        # Hooks & Terrain
        world,
        before,
        after,
        # Step Pattern Types
        custom_type,
        register_custom_type,
        TypeBuilder,
        # The radish parser
        FeatureFileParser,
        # Models
        Feature,
        Rule,
        DefaultRule,
        Background,
        Scenario,
        ScenarioOutline,
        ScenarioLoop,
        Step,
        Tag,
        PreconditionTag,
        ConstantTag,
        # Exception Types
        RadishError,
        # The radish-bdd package version
        __version__,
    )
