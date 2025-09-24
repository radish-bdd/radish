"""
radish
~~~~~~

Behavior Driven Development tool for Python - the root from red to green

Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.customtyperegistry import boolean_type


@pytest.mark.parametrize(
    "input_str, expected_bool",
    [
        # cases from yaml spec
        ("yes", True),
        ("Yes", True),
        ("YES", True),
        ("y", True),
        ("Y", True),
        ("no", False),
        ("No", False),
        ("NO", False),
        ("n", False),
        ("N", False),
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("on", True),
        ("On", True),
        ("ON", True),
        ("off", False),
        ("Off", False),
        ("OFF", False),
        # weird extra cases
        ("0", False),
        ("1", True),
        ("yEahhhh", True),
        ("y  ", True),
    ],
)
def test_boolean_type_parsing(input_str, expected_bool):
    assert boolean_type(input_str) is expected_bool
