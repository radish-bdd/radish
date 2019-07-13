"""
    This module provides a class to represent a Scenario
"""

from .model import Model
from .state import State


class Scenario(Model):
    """
        Represents a Scenario
    """

    def __init__(
        self,
        id,
        keyword,
        sentence,
        path,
        line,
        parent,
        tags=None,
        preconditions=None,
        background=None,
    ):
        super(Scenario, self).__init__(id, keyword, sentence, path, line, parent, tags)
        self.absolute_id = None
        self.preconditions = preconditions or []
        self.background = background
        self.steps = []
        self.context = self.Context()
        self.complete = False

    @property
    def feature(self):
        """Get the Feature for this Scenario"""
        return self.parent

    @property
    def state(self):
        """
            Returns the state of the scenario
        """
        steps = []
        if self.background:
            steps.extend(self.background.steps)

        steps.extend(self.steps)
        for step in steps:
            if step.state is not State.PASSED:
                return step.state
        return State.PASSED

    @property
    def constants(self):
        """
            Returns all constants
        """
        constants = []
        for name, value in self.context.constants:
            for parent_name, parent_value in self.parent.constants:
                value = value.replace("${{{0}}}".format(parent_name), parent_value)
            constants.append((name, value))
        constants.extend(self.parent.constants)
        return constants

    @property
    def all_steps(self):
        """
            Returns all steps from all preconditions in the correct order
        """
        steps = []
        if self.background:
            steps.extend(self.background.all_steps)

        for precondition in self.preconditions:
            steps.extend(precondition.all_steps)
        steps.extend(self.steps)
        return steps

    @property
    def failed_step(self):
        """
            Returns the first failed step
        """
        steps = []
        if self.background:
            steps.extend(self.background.steps)

        steps.extend(self.steps)

        # FIXME(TF): what about Scenario Precondition Steps?

        for step in steps:
            if step.state == State.FAILED:
                return step
        return None

    def has_to_run(self, scenario_choice):
        """
            Returns wheiter the scenario has to run or not

            :param list scenario_choice: the scenarios to run. If None all will run
        """
        if not scenario_choice:
            return True

        return self.absolute_id in (scenario_choice or [])

    def after_parse(self):
        """
            This method is called after the scenario is completely parsed.

            Actions to do:
              * number steps
              * fix parent of precondition steps
        """
        for step_id, step in enumerate(self.all_steps, start=1):
            step.id = step_id
            if step.parent != self:
                # check if step is from background
                if self.background and step in self.background.steps:
                    step.as_background = self.background
                else:
                    step.as_precondition = step.parent
                step.parent = self
        self.complete = True
