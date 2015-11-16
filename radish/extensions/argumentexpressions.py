# -*- coding: utf-8 -*-

"""
    This module provides some default ArgumentExpressions
"""

from radish.argexpregistry import arg_expr


@arg_expr("MathExpression", r"[0-9 +\-*/%.e]+")
def arg_expr_mathexpression(text):
    """
        Argument Expression which expects a valid math expression

        :param str text: the text which was matched as math expression

        :returns: calculated float number from the math expression
        :rtype: float
    """
    return float(eval(text))
