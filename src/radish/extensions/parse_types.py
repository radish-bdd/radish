"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.parsetyperegistry import custom_type


@custom_type("int", r"[-+]?[0-9]+")
def int_type(text):
    """Custom Parse Type to parse an integer value.

    The integer value must be of the format: [-+]?[0-9]+
    """
    return int(text)


@custom_type(
    "float", r"[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?"
)
def float_type(text):
    r"""Custom Parse Type to parse a float value.

    The float value must be of the format:
        [-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?
    """
    return float(text)


@custom_type("word", r"\S+")
def word_type(text):
    r"""Custom Parse Type to parse a word.

    The word value must be of the format: \S+
    """
    return str(text)


@custom_type(
    "bool",
    r"(0|1|yes|Yes|YES|y|Y|no|No|NO|n|N|true|True|TRUE|false|False|FALSE|on|On|ON|off|Off|OFF)",
)
def boolean_type(text):
    """Custom Parse Type to parse a boolean value.

    The same values are parsed as YAML does:
        http://yaml.org/type/bool.html

    Plus 0 and 1
    """
    text = text.lower()
    return text == "1" or text.startswith("y") or text == "true" or text == "on"


@custom_type("QuotedString", r'"(?:[^"\\]|\\.)*"')
def quoted_string_type(text):
    """Custom Parse Type to parse a quoted string.

    Double quotes (") have to be escaped with a
    backslash within the double quotes.
    """
    return text[1:-1]


@custom_type("MathExpression", r"[0-9 +\-*/%.e]+")
def math_expression_type(text):
    """Custom Parse Type which expects a valid mathematical expression

    :param str text: the text which was matched as math expression

    :returns: calculated float number from the math expression
    :rtype: float
    """
    return float(eval(text))
