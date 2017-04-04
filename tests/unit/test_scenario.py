# -*- coding: utf-8 -*-

from tests.base import *

from radish.scenario import Scenario
from radish.background import Background
from radish.stepmodel import Step
from radish.model import Tag


class ScenarioTestCase(RadishTestCase):
    """
        Tests for the scenario model class
    """
    def test_scenario_state(self):
        """
            Test scenario's state
        """
        step_1 = Mock(state=Step.State.UNTESTED)
        step_2 = Mock(state=Step.State.UNTESTED)
        step_3 = Mock(state=Step.State.UNTESTED)

        scenario = Scenario(1, "Scenario", "Some scenario", None, None, None)
        scenario.steps.extend([step_1, step_2, step_3])

        scenario.state.should.be.equal(Step.State.UNTESTED)

        step_1.state = Step.State.SKIPPED
        scenario.state.should.be.equal(Step.State.SKIPPED)

        step_1.state = Step.State.FAILED
        scenario.state.should.be.equal(Step.State.FAILED)

        step_2.state = Step.State.PASSED
        scenario.state.should.be.equal(Step.State.FAILED)

        step_3.state = Step.State.PASSED
        scenario.state.should.be.equal(Step.State.FAILED)

        step_1.state = Step.State.PASSED
        scenario.state.should.be.equal(Step.State.PASSED)

    def test_scenario_constants(self):
        """
            Test scenario's constants
        """
        feature = Mock(constants=[("feature_var_1", "1"), ("feature_var_2", "2")])

        scenario = Scenario(1, "Scenario", "Some scenario", None, None, feature)
        scenario.context.constants.extend([("scenario_var_1", "3"), ("scenario_var_2", "4")])

        scenario.constants.should.have.length_of(4)
        scenario.constants[0].should.be.equal(("scenario_var_1", "3"))
        scenario.constants[1].should.be.equal(("scenario_var_2", "4"))
        scenario.constants[2].should.be.equal(("feature_var_1", "1"))
        scenario.constants[3].should.be.equal(("feature_var_2", "2"))

    def test_scenario_all_steps(self):
        """
        Test getting all steps from scenario
        """
        step_1 = Mock(state=Step.State.UNTESTED)
        step_2 = Mock(state=Step.State.UNTESTED)
        step_3 = Mock(state=Step.State.UNTESTED)

        scenario = Scenario(1, "Scenario", "Some scenario", None, None, None)
        scenario.steps.extend([step_1, step_2, step_3])

        scenario.all_steps.should.have.length_of(3)
        scenario.all_steps[0].should.be.equal(step_1)
        scenario.all_steps[1].should.be.equal(step_2)
        scenario.all_steps[2].should.be.equal(step_3)

        precond_step_1 = Mock(state=Step.State.UNTESTED)
        precond_step_2 = Mock(state=Step.State.UNTESTED)
        scenario_precond = Scenario(2, "Scenario", "Some precond scenario", None, None, None)
        scenario_precond.steps.extend([precond_step_1, precond_step_2])

        scenario.preconditions.append(scenario_precond)

        scenario.all_steps.should.have.length_of(5)
        scenario.all_steps[0].should.be.equal(precond_step_1)
        scenario.all_steps[1].should.be.equal(precond_step_2)
        scenario.all_steps[2].should.be.equal(step_1)
        scenario.all_steps[3].should.be.equal(step_2)
        scenario.all_steps[4].should.be.equal(step_3)

    def test_scenario_get_failed_step(self):
        """
            Test getting first failed step from scenario
        """
        step_1 = Mock(state=Step.State.UNTESTED)
        step_2 = Mock(state=Step.State.UNTESTED)
        step_3 = Mock(state=Step.State.UNTESTED)

        scenario = Scenario(1, "Scenario", "Some scenario", None, None, None)
        scenario.steps.extend([step_1, step_2, step_3])

        scenario.failed_step.should.be.equal(None)

        step_1.state = Step.State.FAILED
        scenario.failed_step.should.be.equal(step_1)

        step_1.state = Step.State.PASSED
        scenario.failed_step.should.be.equal(None)

        step_2.state = Step.State.FAILED
        scenario.failed_step.should.be.equal(step_2)

    def test_scenario_has_to_run(self):
        """
            Test scenario's has to run functionality
        """
        feature = Mock()

        s = Scenario(1, "Scenario", "Some scenario", None, None, feature)
        s.absolute_id = 1
        s.has_to_run.when.called_with(None).should.return_value(True)

        s.has_to_run.when.called_with([1]).should.return_value(True)
        s.has_to_run.when.called_with([1, 2]).should.return_value(True)
        s.has_to_run.when.called_with([2]).should.return_value(False)

    def test_scenario_after_parse_hook(self):
        """
            Test scenario after parse hook
        """
        step_1 = Mock(state=Step.State.UNTESTED, id=1)
        step_2 = Mock(state=Step.State.UNTESTED, id=2)
        step_3 = Mock(state=Step.State.UNTESTED, id=3)
        scenario = Scenario(1, "Scenario", "Some scenario", None, None, None)
        scenario.steps.extend([step_1, step_2, step_3])

        step_1.parent = scenario
        step_2.parent = scenario
        step_3.parent = scenario

        scenario.all_steps.should.have.length_of(3)
        scenario.all_steps[0].should.be.equal(step_1)
        scenario.all_steps[1].should.be.equal(step_2)
        scenario.all_steps[2].should.be.equal(step_3)

        scenario_precond = Scenario(2, "Scenario", "Some precond scenario", None, None, None)
        precond_step_1 = Mock(state=Step.State.UNTESTED, id=1)
        precond_step_2 = Mock(state=Step.State.UNTESTED, id=2)
        scenario_precond.steps.extend([precond_step_1, precond_step_2])

        precond_step_1.parent = scenario_precond
        precond_step_2.parent = scenario_precond

        scenario.preconditions.append(scenario_precond)

        # check before 'after_parse': step id and parent should be wrong
        scenario.all_steps[0].id.should.be.equal(1)
        scenario.all_steps[1].id.should.be.equal(2)
        scenario.all_steps[2].id.should.be.equal(1)
        scenario.all_steps[3].id.should.be.equal(2)
        scenario.all_steps[4].id.should.be.equal(3)
        scenario.all_steps[0].parent.should.be.equal(scenario_precond)
        scenario.all_steps[1].parent.should.be.equal(scenario_precond)
        scenario.all_steps[2].parent.should.be.equal(scenario)
        scenario.all_steps[3].parent.should.be.equal(scenario)
        scenario.all_steps[4].parent.should.be.equal(scenario)

        scenario.after_parse()

        scenario.all_steps[0].id.should.be.equal(1)
        scenario.all_steps[1].id.should.be.equal(2)
        scenario.all_steps[2].id.should.be.equal(3)
        scenario.all_steps[3].id.should.be.equal(4)
        scenario.all_steps[4].id.should.be.equal(5)
        scenario.all_steps[0].parent.should.be.equal(scenario)
        scenario.all_steps[1].parent.should.be.equal(scenario)
        scenario.all_steps[2].parent.should.be.equal(scenario)
        scenario.all_steps[3].parent.should.be.equal(scenario)
        scenario.all_steps[4].parent.should.be.equal(scenario)


    def test_scenario_state_with_background(self):
        """
        Test scenario state with assigned background
        """
        bg_step_1 = Mock(state=Step.State.UNTESTED)
        bg_step_2 = Mock(state=Step.State.UNTESTED)
        bg_step_3 = Mock(state=Step.State.UNTESTED)

        step_1 = Mock(state=Step.State.UNTESTED)
        step_2 = Mock(state=Step.State.UNTESTED)
        step_3 = Mock(state=Step.State.UNTESTED)

        all_steps = [bg_step_1, bg_step_2, bg_step_3, step_1, step_2, step_3]

        # create background and scenario
        background = Background('Background', 'Some Background', None, None, None)
        scenario = Scenario(1, "Scenario", "Some scenario", None, None, None)

        # assign background to scenario
        scenario.background = background

        # assign steps to background and scenario
        background.steps.extend([bg_step_1, bg_step_2, bg_step_3])
        scenario.steps.extend([step_1, step_2, step_3])

        # in the beginning all steps are untested
        scenario.state.should.be.equal(Step.State.UNTESTED)

        # lets set them to passed
        for step in all_steps:
            step.state = Step.State.PASSED

        # the scenario should be passed
        scenario.state.should.be.equal(Step.State.PASSED)

        # let's fail a background step
        bg_step_2.state = Step.State.FAILED
        scenario.state.should.be.equal(Step.State.FAILED)

        # let's skip a background step
        bg_step_2.state = Step.State.SKIPPED
        scenario.state.should.be.equal(Step.State.SKIPPED)


    def test_scenario_all_steps_with_background(self):
        """
        Test scenario all_steps with assigned background
        """
        bg_step_1 = Mock(state=Step.State.UNTESTED)
        bg_step_2 = Mock(state=Step.State.UNTESTED)
        bg_step_3 = Mock(state=Step.State.UNTESTED)

        step_1 = Mock(state=Step.State.UNTESTED)
        step_2 = Mock(state=Step.State.UNTESTED)
        step_3 = Mock(state=Step.State.UNTESTED)

        # create background and scenario
        background = Background('Background', 'Some Background', None, None, None)
        scenario = Scenario(1, "Scenario", "Some scenario", None, None, None)

        # assign background to scenario
        scenario.background = background

        # assign steps to background and scenario
        background.steps.extend([bg_step_1, bg_step_2, bg_step_3])
        scenario.steps.extend([step_1, step_2, step_3])

        # in the beginning all steps are untested
        all_steps = scenario.all_steps
        all_steps.should.have.length_of(6)
        all_steps[0].should.be(bg_step_1)
        all_steps[3].should.be(step_1)


    def test_scenario_failed_step_with_background(self):
        """
        Test scenario failed step with assigned background
        """
        bg_step_1 = Mock(state=Step.State.UNTESTED)
        bg_step_2 = Mock(state=Step.State.UNTESTED)
        bg_step_3 = Mock(state=Step.State.UNTESTED)

        step_1 = Mock(state=Step.State.UNTESTED)
        step_2 = Mock(state=Step.State.UNTESTED)
        step_3 = Mock(state=Step.State.UNTESTED)

        all_steps = [bg_step_1, bg_step_2, bg_step_3, step_1, step_2, step_3]

        # create background and scenario
        background = Background('Background', 'Some Background', None, None, None)
        scenario = Scenario(1, "Scenario", "Some scenario", None, None, None)

        # assign background to scenario
        scenario.background = background

        # assign steps to background and scenario
        background.steps.extend([bg_step_1, bg_step_2, bg_step_3])
        scenario.steps.extend([step_1, step_2, step_3])

        # in the beginning all steps are untested
        scenario.state.should.be.equal(Step.State.UNTESTED)

        # lets set them to passed
        for step in all_steps:
            step.state = Step.State.PASSED

        # the scenario should be passed
        scenario.failed_step.should.be.none

        # let's fail a background step
        bg_step_2.state = Step.State.FAILED
        scenario.failed_step.should.be(bg_step_2)
