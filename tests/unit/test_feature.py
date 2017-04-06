# -*- coding: utf-8 -*-

from tests.base import *

from radish.feature import Feature
from radish.scenario import Scenario
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.stepmodel import Step
from radish.main import setup_config
from radish.model import Tag


class FeatureTestCase(RadishTestCase):
    """
        Tests for the feature model class
    """
    @classmethod
    def setUpClass(cls):
        """
            Setup config object
        """
        setup_config({
            "--early_exit": False,
            "--debug-steps": False,
            "--debug-after-failure": False,
            "--inspect-after-failure": False,
            "--bdd-xml": False,
            "--no-ansi": False,
            "--no-line-jump": False,
            "--write-steps-once": False,
            "--scenarios": None,
            "--shuffle": False,
            "--write-ids": False,
            "--tags": None,
            "--expand": True,
        })

    def test_feature_all_scenarios(self):
        """
            Test getting all scenario from feature
        """
        feature = Feature(1, "Feature", "Some feature", None, None)

        scenario_1 = Mock(spec=Scenario)
        scenario_outline_1_example_1 = Mock(spec=Scenario)
        scenario_outline_1_example_2 = Mock(spec=Scenario)
        scenario_outline_1 = Mock(spec=ScenarioOutline, scenarios=[scenario_outline_1_example_1, scenario_outline_1_example_2])
        scenario_loop_1_example_1 = Mock(spec=Scenario)
        scenario_loop_1_example_2 = Mock(spec=Scenario)
        scenario_loop_1 = Mock(spec=ScenarioLoop, scenarios=[scenario_loop_1_example_1, scenario_loop_1_example_2])
        scenario_2 = Mock(spec=Scenario)

        feature.scenarios.extend([scenario_1, scenario_outline_1, scenario_loop_1, scenario_2])

        feature.all_scenarios.should.have.length_of(8)
        feature.all_scenarios[0].should.be.equal(scenario_1)
        feature.all_scenarios[1].should.be.equal(scenario_outline_1)
        feature.all_scenarios[2].should.be.equal(scenario_outline_1_example_1)
        feature.all_scenarios[3].should.be.equal(scenario_outline_1_example_2)
        feature.all_scenarios[4].should.be.equal(scenario_loop_1)
        feature.all_scenarios[5].should.be.equal(scenario_loop_1_example_1)
        feature.all_scenarios[6].should.be.equal(scenario_loop_1_example_2)
        feature.all_scenarios[7].should.be.equal(scenario_2)

    def test_feature_representations(self):
        """
            Test feature representations
        """
        feature = Feature(1, "Feature", "Some feature", "sometest.feature", 1)
        str(feature).should.be.equal("Feature: Some feature from sometest.feature:1")
        repr(feature).should.be.equal("<Feature: Some feature from sometest.feature:1>")

    def test_feature_scenario_iterator(self):
        """
            Test using a feature as iterator which iterates over its scenarios
        """
        feature = Feature(1, "Feature", "Some feature", None, None)
        feature.scenarios.append(Mock(id=1))
        feature.scenarios.append(Mock(id=2))
        feature.scenarios.append(Mock(id=3))
        feature.scenarios.append(Mock(id=4))

        for expected_scenario_id, scenario in enumerate(feature, start=1):
            scenario.id.should.be.equal(expected_scenario_id)

    def test_feature_get_scenario_by_sentence(self):
        """
            Test getting scenario by sentence from feature
        """
        feature = Feature(1, "Feature", "Some feature", None, None)
        scenario_1 = Mock(sentence="First scenario")
        scenario_2 = Mock(sentence="Second scenario")
        scenario_3 = Mock(sentence="Third scenario")
        feature.scenarios.extend([scenario_1, scenario_2, scenario_3])

        feature["First scenario"].should.be.equal(scenario_1)
        feature["Second scenario"].should.be.equal(scenario_2)
        feature["Third scenario"].should.be.equal(scenario_3)

    def test_feature_state(self):
        """
            Test getting the state of a feature
        """
        feature = Feature(1, "Feature", "Some feature", None, None)
        scenario_1 = Mock(state=Step.State.UNTESTED)
        scenario_2 = Mock(state=Step.State.UNTESTED)
        scenario_outline = Mock(spec=ScenarioOutline, scenarios=[])
        scenario_loop = Mock(spec=ScenarioLoop, scenarios=[])
        scenario_3 = Mock(state=Step.State.UNTESTED)
        feature.scenarios.extend([scenario_1, scenario_2, scenario_outline, scenario_loop, scenario_3])

        feature.state.should.be.equal(Step.State.UNTESTED)

        scenario_1.state = Step.State.SKIPPED
        feature.state.should.be.equal(Step.State.SKIPPED)

        scenario_1.state = Step.State.FAILED
        feature.state.should.be.equal(Step.State.FAILED)

        scenario_2.state = Step.State.PASSED
        feature.state.should.be.equal(Step.State.FAILED)

        scenario_3.state = Step.State.PASSED
        feature.state.should.be.equal(Step.State.FAILED)

        scenario_1.state = Step.State.PASSED
        feature.state.should.be.equal(Step.State.PASSED)

    def test_feature_has_to_run(self):
        """
            Test feature's has to run functionality
        """
        f = Feature(1, "Feature", "Some feature", None, None)
        f.has_to_run.when.called_with(None).should.return_value(True)

        f.scenarios.append(Mock(absolute_id=1, has_to_run=lambda x: False))
        f.scenarios.append(Mock(absolute_id=2, has_to_run=lambda x: False))
        f.scenarios.append(Mock(absolute_id=3, has_to_run=lambda x: False))

        f.has_to_run.when.called_with([1]).should.return_value(True)
        f.has_to_run.when.called_with([1, 2]).should.return_value(True)
        f.has_to_run.when.called_with([3]).should.return_value(True)
        f.has_to_run.when.called_with([1, 4]).should.return_value(True)
        f.has_to_run.when.called_with([5, 4]).should.return_value(False)
        f.has_to_run.when.called_with([6]).should.return_value(False)
