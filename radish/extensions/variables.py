# -*- coding: utf-8 -*-

"""
    This module brings the benefit of variables to radish
"""

from radish.step import step
from radish.argexpregistry import ArgumentExpression


@step(ArgumentExpression(r"I set the variable {variable_name:VariableName} to {value:MathExpression}"))
def set_float_variable_step(step, variable_name, value):  # pylint: disable=redefined-outer-name
    """
        Sets the variable `variable_name` in the scenario context to the float value `value`

        :param str variable_name: the name of the variable
        :param float value: the value for the variable
    """
    setattr(step.context, variable_name, value)


@step(ArgumentExpression(r"I set the variable {variable_name:VariableName} to \"{value}\""))
def set_str_variable_step(step, variable_name, value):  # pylint: disable=redefined-outer-name
    """
        Sets the variable `variable_name` in the scenario context to the string `value`

        :param str variable_name: the name of the variable
        :param str value: the value for the variable
    """
    setattr(step.context, variable_name, value)
