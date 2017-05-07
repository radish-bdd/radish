# -*- coding: utf-8 -*-

"""
This module provides some default custom types
"""

from radish.customtyperegistry import custom_type


@custom_type("MathExpression", r"[0-9 +\-*/%.e]+")
def math_expression_type(text):
    """
        Custom Type which expects a valid math expression

        :param str text: the text which was matched as math expression

        :returns: calculated float number from the math expression
        :rtype: float
    """
    return float(eval(text))
