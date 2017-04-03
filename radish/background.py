# -*- coding: utf-8 -*-

"""
This module provides a representation of a Feature Background.
"""

from .scenario import Scenario
from .stepmodel import Step


class Background(Scenario):
    """
    Represents a Background
    """
    def __init__(self, keyword, sentence, path, line, parent):
        super(Background, self).__init__(None, keyword, sentence, path, line, parent)

    def create_instance(self, parent=None, steps_runable=False):
        """
        Return a copy of this Background instance.
        This enables a scenario to operate on the steps
        without influencing all the other copies.
        """
        background = Background(self.keyword, self.sentence, self.path, self.line, parent)

        for step in self.all_steps:
            # FIXME(TF): move to Step.copy
            step_copy = Step(step.id, step.sentence, step.path, step.line, parent, steps_runable)
            step_copy.table = step.table
            step_copy.raw_text = step.raw_text
            background.steps.append(step_copy)

        return background
