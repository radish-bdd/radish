# -*- coding: utf-8 -*-

"""
    This module provides some default ArgumentExpressions
"""

from radish.argexpregistry import arg_expr, ArgumentExpression


@arg_expr("Number", r"(\+|-)?\d+")
def arg_expr_number(text):
    """
        Argument Expression which expects a valid number

        :param str text: the text which was matched as number

        :returns: integer number
        :rtype: int
    """
    return int(text)


@arg_expr("FloatNumber", r"(\+|-)?\d+(\.\d+)?")
def arg_expr_floatnumber(text):
    """
        Argument Expression which expects a valid floating point number

        :param str text: the text which was matched as floating point number

        :returns: float number
        :rtype: float
    """
    return float(text)


@arg_expr("MathExpression", r"[0-9 +\-*/%.e]+")
def arg_expr_mathexpression(text):
    """
        Argument Expression which expects a valid math expression

        :param str text: the text which was matched as math expression

        :returns: calculated float number from the math expression
        :rtype: float
    """
    return float(eval(text))


@arg_expr("VariableName", r"[A-Za-z_][A-Za-z0-9_]*")
def arg_expr_variablename(text):
    """
        Argument Expression which expects a variable name

        :param str text: the text which was matched as variable name

        :returns: the variable name
        :rtype: str
    """
    return text
