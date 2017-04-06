# -*- coding: utf-8 -*-

from tests.base import *

from tempfile import NamedTemporaryFile
import tagexpressions

from radish.parser import FeatureParser
from radish.feature import Feature
from radish.scenario import Scenario
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.exceptions import RadishError, LanguageNotSupportedError, FeatureFileSyntaxError


class ParserTestCase(RadishTestCase):
    """
        Tests for the parser class
    """
    def test_language_loading(self):
        """
            Test loading of a specific language
        """
        core = Mock()
        en_feature_parser = FeatureParser(core, "/", 1, language="en")
        en_feature_parser.keywords.feature.should.be.equal("Feature")
        en_feature_parser.keywords.scenario.should.be.equal("Scenario")
        en_feature_parser.keywords.scenario_outline.should.be.equal("Scenario Outline")
        en_feature_parser.keywords.examples.should.be.equal("Examples")

        de_feature_parser = FeatureParser(core, "/", 1, language="de")
        de_feature_parser.keywords.scenario.should.be.equal("Szenario")
        de_feature_parser.keywords.scenario_outline.should.be.equal("Szenario Auslagerung")
        de_feature_parser.keywords.examples.should.be.equal("Beispiele")

        FeatureParser.when.called_with(core, "/", 1, language="foo").should.throw(LanguageNotSupportedError)

    def test_parse_unexisting_featurefile(self):
        """
            Test parsing of an unexisting featurefile
        """
        core = Mock()
        FeatureParser.when.called_with(core, "nonexisting.feature", 1).should.throw(OSError, "Feature file at 'nonexisting.feature' does not exist")

    def test_parse_empty_featurefile(self):
        """
            Test parsing of an empty feature file
        """
        core = Mock()
        with NamedTemporaryFile("w+") as featurefile:
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse.when.called_with().should.throw(RadishError, "No Feature found in file {0}".format(featurefile.name))

    def test_parse_empty_feature(self):
        """
            Test parsing of an empty feature
        """
        feature = """Feature: some empty feature"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.sentence.should.be.equal("some empty feature")
            parser.feature.id.should.be.equal(1)
            parser.feature.path.should.be.equal(featurefile.name)
            parser.feature.line.should.be.equal(1)
            parser.feature.scenarios.should.be.empty

    def test_parse_empty_feature_with_description(self):
        """
            Test parsing of an empty feature with desription
        """
        feature = """Feature: some empty feature
    In order to support cool software
    I do fancy BDD testing with radish"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.sentence.should.be.equal("some empty feature")
            parser.feature.id.should.be.equal(1)
            parser.feature.path.should.be.equal(featurefile.name)
            parser.feature.line.should.be.equal(1)
            parser.feature.scenarios.should.be.empty
            parser.feature.description.should.have.length_of(2)
            parser.feature.description[0].should.be.equal("In order to support cool software")
            parser.feature.description[1].should.be.equal("I do fancy BDD testing with radish")

    def test_parse_featurefile_with_multiple_features(self):
        """
            Test parsing a feature file with multiple features
        """
        feature = """Feature: some empty feature
Feature: another empty feature"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse.when.called_with().should.throw(RadishError, "radish supports only one Feature per feature file")

    def test_parse_feature_with_empty_scenario(self):
        """
            Test parsing of a feature with one empty scenario
        """
        feature = """Feature: some feature
    Scenario: some empty scenario"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.id.should.be.equal(1)
            parser.feature.sentence.should.be.equal("some feature")
            parser.feature.scenarios.should.have.length_of(1)
            parser.feature.scenarios[0].id.should.be.equal(1)
            parser.feature.scenarios[0].sentence.should.be.equal("some empty scenario")
            parser.feature.scenarios[0].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].line.should.be.equal(2)
            parser.feature.scenarios[0].steps.should.be.empty

    def test_parse_feature_with_one_scenario_and_steps(self):
        """
            Test parsing of a feautre with one scenario and multiple steps
        """
        feature = """Feature: some feature
    Scenario: some fancy scenario
        Given I have the number 5
        When I add 2 to my number
        Then I expect my number to be 7 """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.id.should.be.equal(1)
            parser.feature.sentence.should.be.equal("some feature")
            parser.feature.scenarios.should.have.length_of(1)
            parser.feature.scenarios.should.have.length_of(1)
            parser.feature.scenarios[0].sentence.should.be.equal("some fancy scenario")

            parser.feature.scenarios[0].steps.should.have.length_of(3)
            parser.feature.scenarios[0].steps[0].id.should.be.equal(1)
            parser.feature.scenarios[0].steps[0].sentence.should.be.equal("Given I have the number 5")
            parser.feature.scenarios[0].steps[0].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[0].line.should.be.equal(3)
            parser.feature.scenarios[0].steps[1].id.should.be.equal(2)
            parser.feature.scenarios[0].steps[1].sentence.should.be.equal("When I add 2 to my number")
            parser.feature.scenarios[0].steps[1].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[1].line.should.be.equal(4)
            parser.feature.scenarios[0].steps[2].id.should.be.equal(3)
            parser.feature.scenarios[0].steps[2].sentence.should.be.equal("Then I expect my number to be 7")
            parser.feature.scenarios[0].steps[2].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[2].line.should.be.equal(5)

    def test_parse_feature_with_multiple_scenarios(self):
        """
            Test parsing of a feature with multiple scenarios and steps
        """
        feature = """Feature: some feature
    Scenario: some fancy scenario
        Given I have the number 5
        When I add 2 to my number
        Then I expect my number to be 7

    Scenario: some other fancy scenario
        Given I have the number 50
        When I add 20 to my number
        Then I expect my number to be 70"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.id.should.be.equal(1)
            parser.feature.sentence.should.be.equal("some feature")
            parser.feature.scenarios.should.have.length_of(2)

            parser.feature.scenarios[0].id.should.be.equal(1)
            parser.feature.scenarios[0].sentence.should.be.equal("some fancy scenario")
            parser.feature.scenarios[0].steps.should.have.length_of(3)
            parser.feature.scenarios[0].steps[0].id.should.be.equal(1)
            parser.feature.scenarios[0].steps[0].sentence.should.be.equal("Given I have the number 5")
            parser.feature.scenarios[0].steps[0].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[0].line.should.be.equal(3)
            parser.feature.scenarios[0].steps[1].id.should.be.equal(2)
            parser.feature.scenarios[0].steps[1].sentence.should.be.equal("When I add 2 to my number")
            parser.feature.scenarios[0].steps[1].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[1].line.should.be.equal(4)
            parser.feature.scenarios[0].steps[2].id.should.be.equal(3)
            parser.feature.scenarios[0].steps[2].sentence.should.be.equal("Then I expect my number to be 7")
            parser.feature.scenarios[0].steps[2].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[2].line.should.be.equal(5)

            parser.feature.scenarios[1].id.should.be.equal(2)
            parser.feature.scenarios[1].sentence.should.be.equal("some other fancy scenario")
            parser.feature.scenarios[1].steps.should.have.length_of(3)
            parser.feature.scenarios[1].steps[0].id.should.be.equal(1)
            parser.feature.scenarios[1].steps[0].sentence.should.be.equal("Given I have the number 50")
            parser.feature.scenarios[1].steps[0].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[1].steps[0].line.should.be.equal(8)
            parser.feature.scenarios[1].steps[1].id.should.be.equal(2)
            parser.feature.scenarios[1].steps[1].sentence.should.be.equal("When I add 20 to my number")
            parser.feature.scenarios[1].steps[1].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[1].steps[1].line.should.be.equal(9)
            parser.feature.scenarios[1].steps[2].id.should.be.equal(3)
            parser.feature.scenarios[1].steps[2].sentence.should.be.equal("Then I expect my number to be 70")
            parser.feature.scenarios[1].steps[2].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[1].steps[2].line.should.be.equal(10)

    def test_feature_with_comments(self):
        """
            Test parsing a feature with comments
        """
        feature = """Feature: some feature
    # this is a comment
    Scenario: some fancy scenario
        Given I have the number 5
        When I add 2 to my number
        # this is another comment
        Then I expect my number to be 7

    Scenario: some other fancy scenario
        Given I have the number 50
        # foobar comment
        When I add 20 to my number
        Then I expect my number to be 70
        # another stupid comment"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.sentence.should.be.equal("some feature")
            parser.feature.scenarios.should.have.length_of(2)

            parser.feature.scenarios[0].sentence.should.be.equal("some fancy scenario")
            parser.feature.scenarios[0].line.should.be.equal(3)
            parser.feature.scenarios[0].steps.should.have.length_of(3)
            parser.feature.scenarios[0].steps[0].sentence.should.be.equal("Given I have the number 5")
            parser.feature.scenarios[0].steps[0].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[0].line.should.be.equal(4)
            parser.feature.scenarios[0].steps[1].sentence.should.be.equal("When I add 2 to my number")
            parser.feature.scenarios[0].steps[1].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[1].line.should.be.equal(5)
            parser.feature.scenarios[0].steps[2].sentence.should.be.equal("Then I expect my number to be 7")
            parser.feature.scenarios[0].steps[2].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[0].steps[2].line.should.be.equal(7)

            parser.feature.scenarios[1].sentence.should.be.equal("some other fancy scenario")
            parser.feature.scenarios[1].line.should.be.equal(9)
            parser.feature.scenarios[1].steps.should.have.length_of(3)
            parser.feature.scenarios[1].steps[0].sentence.should.be.equal("Given I have the number 50")
            parser.feature.scenarios[1].steps[0].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[1].steps[0].line.should.be.equal(10)
            parser.feature.scenarios[1].steps[1].sentence.should.be.equal("When I add 20 to my number")
            parser.feature.scenarios[1].steps[1].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[1].steps[1].line.should.be.equal(12)
            parser.feature.scenarios[1].steps[2].sentence.should.be.equal("Then I expect my number to be 70")
            parser.feature.scenarios[1].steps[2].path.should.be.equal(featurefile.name)
            parser.feature.scenarios[1].steps[2].line.should.be.equal(13)

    def test_parse_feature_with_scenario_outline(self):
        """
            Test parsing of a feature file with a scenario outline
        """
        feature = """Feature: some feature
    Scenario Outline: some fancy scenario
        Given I have the number <number>
        When I add <delta> to my number
        Then I expect my number to be <result>

    Examples:
        | number | delta | result |
        | 5      | 2     | 7      |
        | 10     | 3     | 13     |
        | 15     | 6     | 21     |
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.id.should.be.equal(1)
            parser.feature.sentence.should.be.equal("some feature")
            parser.feature.scenarios.should.have.length_of(1)

            scenario = parser.feature.scenarios[0]
            scenario.should.be.a(ScenarioOutline)
            scenario.id.should.be.equal(1)
            scenario.sentence.should.be.equal("some fancy scenario")

            scenario.steps.should.have.length_of(3)
            scenario.steps[0].id.should.be.equal(1)
            scenario.steps[0].sentence.should.be.equal("Given I have the number <number>")
            scenario.steps[0].path.should.be.equal(featurefile.name)
            scenario.steps[0].line.should.be.equal(3)
            scenario.steps[1].id.should.be.equal(2)
            scenario.steps[1].sentence.should.be.equal("When I add <delta> to my number")
            scenario.steps[1].path.should.be.equal(featurefile.name)
            scenario.steps[1].line.should.be.equal(4)
            scenario.steps[2].id.should.be.equal(3)
            scenario.steps[2].sentence.should.be.equal("Then I expect my number to be <result>")
            scenario.steps[2].path.should.be.equal(featurefile.name)
            scenario.steps[2].line.should.be.equal(5)

            scenario.examples_header.should.be.equal(["number", "delta", "result"])
            scenario.examples.should.have.length_of(3)
            scenario.examples[0].data.should.be.equal(["5", "2", "7"])
            scenario.examples[1].data.should.be.equal(["10", "3", "13"])
            scenario.examples[2].data.should.be.equal(["15", "6", "21"])

            scenario.scenarios.should.have.length_of(3)
            scenario.scenarios[0].id.should.be.equal(2)
            scenario.scenarios[0].steps.should.have.length_of(3)
            scenario.scenarios[0].steps[0].id.should.be.equal(1)
            scenario.scenarios[0].steps[0].sentence.should.be.equal("Given I have the number 5")
            scenario.scenarios[0].steps[1].id.should.be.equal(2)
            scenario.scenarios[0].steps[1].sentence.should.be.equal("When I add 2 to my number")
            scenario.scenarios[0].steps[2].id.should.be.equal(3)
            scenario.scenarios[0].steps[2].sentence.should.be.equal("Then I expect my number to be 7")

            scenario.scenarios[1].id.should.be.equal(3)
            scenario.scenarios[1].steps.should.have.length_of(3)
            scenario.scenarios[0].steps[0].id.should.be.equal(1)
            scenario.scenarios[1].steps[0].sentence.should.be.equal("Given I have the number 10")
            scenario.scenarios[1].steps[1].id.should.be.equal(2)
            scenario.scenarios[1].steps[1].sentence.should.be.equal("When I add 3 to my number")
            scenario.scenarios[1].steps[2].id.should.be.equal(3)
            scenario.scenarios[1].steps[2].sentence.should.be.equal("Then I expect my number to be 13")

            scenario.scenarios[2].id.should.be.equal(4)
            scenario.scenarios[2].steps.should.have.length_of(3)
            scenario.scenarios[2].steps[0].id.should.be.equal(1)
            scenario.scenarios[2].steps[0].sentence.should.be.equal("Given I have the number 15")
            scenario.scenarios[2].steps[1].id.should.be.equal(2)
            scenario.scenarios[2].steps[1].sentence.should.be.equal("When I add 6 to my number")
            scenario.scenarios[2].steps[2].id.should.be.equal(3)
            scenario.scenarios[2].steps[2].sentence.should.be.equal("Then I expect my number to be 21")

    def test_parse_feature_with_scenario_and_scenario_outline(self):
        """
            Test parsing of a feature file with a scenario and a scenario outline
        """
        feature = """Feature: some feature
    Scenario: some normal scenario
        Given I do some stuff
        When I modify it
        Then I expect something else

    Scenario Outline: some fancy scenario
        Given I have the number <number>
        When I add <delta> to my number
        Then I expect my number to be <result>

    Examples:
        | number | delta | result |
        | 5      | 2     | 7      |
        | 10     | 3     | 13     |
        | 15     | 6     | 21     |

    Scenario: some other normal scenario
        Given I do some other stuff
        When I modify it
        Then I expect something else
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.id.should.be.equal(1)
            parser.feature.sentence.should.be.equal("some feature")
            parser.feature.scenarios.should.have.length_of(3)

            parser.feature.scenarios[0].should.be.a(Scenario)
            parser.feature.scenarios[0].id.should.be.equal(1)
            parser.feature.scenarios[0].sentence.should.be.equal("some normal scenario")
            parser.feature.scenarios[0].steps.should.have.length_of(3)
            parser.feature.scenarios[0].steps[0].sentence.should.be.equal("Given I do some stuff")
            parser.feature.scenarios[0].steps[1].sentence.should.be.equal("When I modify it")
            parser.feature.scenarios[0].steps[2].sentence.should.be.equal("Then I expect something else")

            parser.feature.scenarios[1].should.be.a(ScenarioOutline)
            parser.feature.scenarios[1].id.should.be.equal(2)
            parser.feature.scenarios[1].sentence.should.be.equal("some fancy scenario")
            parser.feature.scenarios[1].steps.should.have.length_of(3)
            parser.feature.scenarios[1].steps[0].sentence.should.be.equal("Given I have the number <number>")
            parser.feature.scenarios[1].steps[1].sentence.should.be.equal("When I add <delta> to my number")
            parser.feature.scenarios[1].steps[2].sentence.should.be.equal("Then I expect my number to be <result>")

            parser.feature.scenarios[1].examples_header.should.be.equal(["number", "delta", "result"])
            parser.feature.scenarios[1].examples.should.have.length_of(3)
            parser.feature.scenarios[1].examples[0].data.should.be.equal(["5", "2", "7"])
            parser.feature.scenarios[1].examples[1].data.should.be.equal(["10", "3", "13"])
            parser.feature.scenarios[1].examples[2].data.should.be.equal(["15", "6", "21"])

            parser.feature.scenarios[2].should.be.a(Scenario)
            parser.feature.scenarios[2].id.should.be.equal(6)
            parser.feature.scenarios[2].sentence.should.be.equal("some other normal scenario")
            parser.feature.scenarios[2].steps.should.have.length_of(3)
            parser.feature.scenarios[2].steps[0].sentence.should.be.equal("Given I do some other stuff")
            parser.feature.scenarios[2].steps[1].sentence.should.be.equal("When I modify it")
            parser.feature.scenarios[2].steps[2].sentence.should.be.equal("Then I expect something else")

    def test_parse_feature_with_scenario_and_examples(self):
        """
            Test parsing of a feature with a scenario which has examples
        """
        feature = """Feature: some feature
    Scenario: some fancy scenario
        Given I have the number <number>
        When I add <delta> to my number
        Then I expect my number to be <result>

    Examples:
        | number | delta | result |
        | 5      | 2     | 7      |
        | 10     | 3     | 13     |
        | 15     | 6     | 21     |
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse.when.called_with().should.throw(RadishError, "Scenario does not support Examples. Use 'Scenario Outline'")

    def test_parse_steps_with_table(self):
        """
            Test parsing of a feature with a scenario and steps with a table
        """
        feature = """Feature: some feature
    Scenario: some normal scenario
        Given I have the user
            | Bruce     | Wayne      | Batman      |
            | Chuck     | Norris     | PureAwesome |
            | Peter     | Parker     | Spiderman   |
        When I register them in the database
        Then I expect 3 entries in the database
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.sentence.should.be.equal("some feature")
            parser.feature.scenarios.should.have.length_of(1)

            parser.feature.scenarios[0].should.be.a(Scenario)
            parser.feature.scenarios[0].sentence.should.be.equal("some normal scenario")
            parser.feature.scenarios[0].steps.should.have.length_of(3)
            parser.feature.scenarios[0].steps[0].sentence.should.be.equal("Given I have the user")
            parser.feature.scenarios[0].steps[0].table.should.have.length_of(3)
            parser.feature.scenarios[0].steps[0].table[0].should.be.equal(["Bruce", "Wayne", "Batman"])
            parser.feature.scenarios[0].steps[0].table[1].should.be.equal(["Chuck", "Norris", "PureAwesome"])
            parser.feature.scenarios[0].steps[0].table[2].should.be.equal(["Peter", "Parker", "Spiderman"])

            parser.feature.scenarios[0].steps[1].sentence.should.be.equal("When I register them in the database")
            parser.feature.scenarios[0].steps[1].table.should.have.length_of(0)

            parser.feature.scenarios[0].steps[2].sentence.should.be.equal("Then I expect 3 entries in the database")
            parser.feature.scenarios[0].steps[2].table.should.have.length_of(0)

    def test_detect_scenario_loop(self):
        """
            Test detecting ScenarioLoop on a given line
        """
        line = "Scenario Loop 10: Some fancy scenario loop"

        with NamedTemporaryFile("w+") as featurefile:
            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            result = parser._detect_scenario_loop(line)

            result.should.be.a(tuple)
            result[0].should.be.equal("Some fancy scenario loop")
            result[1].should.be.equal(10)

            parser._detect_scenario_loop.when.called_with("").should.return_value(None)
            parser._detect_scenario_loop.when.called_with("Scenario: Some fancy scenario").should.return_value(None)
            parser._detect_scenario_loop.when.called_with("Scenario Outline: Some fancy scenario").should.return_value(None)
            parser._detect_scenario_loop.when.called_with("Scenario Loop: Some fancy scenario").should.return_value(None)
            parser._detect_scenario_loop.when.called_with("Scenario Loop 5.5: Some fancy scenario").should.return_value(None)

    def test_parse_feature_with_scenario_loop(self):
        """
            Test parsing of a feature file with a scenario loop
        """
        feature = """Feature: some feature
    Scenario Loop 10: some fancy scenario
        Given I have the number 1
        When I add 2 to my number
        Then I expect my number to be 3
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.id.should.be.equal(1)
            parser.feature.sentence.should.be.equal("some feature")
            parser.feature.scenarios.should.have.length_of(1)

            scenario = parser.feature.scenarios[0]
            scenario.should.be.a(ScenarioLoop)
            scenario.id.should.be.equal(1)
            scenario.sentence.should.be.equal("some fancy scenario")

            scenario.steps.should.have.length_of(3)
            scenario.steps[0].id.should.be.equal(1)
            scenario.steps[0].sentence.should.be.equal("Given I have the number 1")
            scenario.steps[0].path.should.be.equal(featurefile.name)
            scenario.steps[0].line.should.be.equal(3)
            scenario.steps[1].id.should.be.equal(2)
            scenario.steps[1].sentence.should.be.equal("When I add 2 to my number")
            scenario.steps[1].path.should.be.equal(featurefile.name)
            scenario.steps[1].line.should.be.equal(4)
            scenario.steps[2].id.should.be.equal(3)
            scenario.steps[2].sentence.should.be.equal("Then I expect my number to be 3")
            scenario.steps[2].path.should.be.equal(featurefile.name)
            scenario.steps[2].line.should.be.equal(5)

            scenario.scenarios.should.have.length_of(10)
            for i in range(10):
                scenario.scenarios[i].id.should.be.equal(i + 2)
                scenario.scenarios[i].steps.should.have.length_of(3)
                scenario.scenarios[i].steps[0].id.should.be.equal(1)
                scenario.scenarios[i].steps[0].sentence.should.be.equal("Given I have the number 1")
                scenario.scenarios[i].steps[1].id.should.be.equal(2)
                scenario.scenarios[i].steps[1].sentence.should.be.equal("When I add 2 to my number")
                scenario.scenarios[i].steps[2].id.should.be.equal(3)
                scenario.scenarios[i].steps[2].sentence.should.be.equal("Then I expect my number to be 3")

    def test_detect_tag(self):
        """
            Test detecting a tag
        """
        feature = """Feature: some feature"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser._detect_tag.when.called_with("@some_tag").should.return_value(("some_tag", None))
            parser._detect_tag.when.called_with("@some_tag sdfg").should.return_value(("some_tag", None))
            parser._detect_tag.when.called_with("@some_tag_with_arg(args)").should.return_value(("some_tag_with_arg", "args"))
            parser._detect_tag.when.called_with("some_tag").should.return_value(None)
            parser._detect_tag.when.called_with("some_tag sdfg").should.return_value(None)

    def test_parse_feature_with_tag(self):
        """
            Test parsing feature with tag
        """
        feature = """
@some_feature
Feature: some feature
    Scenario Loop 10: some fancy scenario
        Given I have the number 1
        When I add 2 to my number
        Then I expect my number to be 3
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.tags.should.have.length_of(1)
            parser.feature.tags[0].name.should.be.equal("some_feature")

    def test_parse_feature_with_multiple_tags(self):
        """
            Test parsing feature with tags
        """
        feature = """
@some_feature
@has_scenario_loop
@add_numbers
Feature: some feature
    Scenario Loop 10: some fancy scenario
        Given I have the number 1
        When I add 2 to my number
        Then I expect my number to be 3
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.tags.should.have.length_of(3)
            parser.feature.tags[0].name.should.be.equal("some_feature")
            parser.feature.tags[1].name.should.be.equal("has_scenario_loop")
            parser.feature.tags[2].name.should.be.equal("add_numbers")

    def test_parse_feature_with_scenario_with_tags(self):
        """
            Test parsing feature with scenario and multiple tags
        """
        feature = """
@some_feature
Feature: some feature
    @some_scenario_loop
    Scenario Loop 10: some fancy scenario
        Given I have the number 1
        When I add 2 to my number
        Then I expect my number to be 3

    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special

    @error_case
    @bad_case
    Scenario: bad case
        Given I have the number 1
        When I add 3 to my number
        Then I expect my number not to be 4
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            parser.feature.tags.should.have.length_of(1)
            parser.feature.tags[0].name.should.be.equal("some_feature")

            parser.feature.scenarios.should.have.length_of(3)

            parser.feature.scenarios[0].tags.should.have.length_of(1)
            parser.feature.scenarios[0].tags[0].name.should.be.equal("some_scenario_loop")

            parser.feature.scenarios[1].tags.should.be.empty

            parser.feature.scenarios[2].tags.should.have.length_of(2)
            parser.feature.scenarios[2].tags[0].name.should.be.equal("error_case")
            parser.feature.scenarios[2].tags[1].name.should.be.equal("bad_case")

    def test_parse_feature_with_ignored_tag(self):
        """
            Test parsing a feature which is not part of the feature tag expression
        """
        feature = """
@some_feature
Feature: some feature
    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1, tag_expr=tagexpressions.parse('not some_feature'))
            feature = parser.parse()

            feature.should.be.none

    def test_parse_feature_with_ignored_scenario(self):
        """
            Test parsing a feature which has an ignored scenario by a given tag expression
        """
        feature = """
Feature: some feature
    @good_case
    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special

    @bad_case
    Scenario: bad case
        Given I have the number 1
        When I add 3 to my number
        Then I expect my number not to be 4

    @good_case
    Scenario: foo second it
        When I have a normal scenario
        Then I expect nothing special

    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1, tag_expr=tagexpressions.parse('not bad_case'))
            feature = parser.parse()

            feature.scenarios.should.have.length_of(2)

    def test_parse_scenario_tag_inheritance(self):
        """
            Test parsing a Scenario which inherits tags
        """
        feature = """
@foo
Feature: some feature
    @good_case
    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special

    @bad_case
    Scenario: bad case
        Given I have the number 1
        When I add 3 to my number
        Then I expect my number not to be 4

    @good_case
    Scenario: foo second it
        When I have a normal scenario
        Then I expect nothing special

    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()

            # expect all three Scenarios parsed
            parser = FeatureParser(core, featurefile.name, 1, tag_expr=tagexpressions.parse('foo'))
            feature = parser.parse()
            feature.scenarios.should.have.length_of(3)

            # expect only good case Scenarios parsed
            parser = FeatureParser(core, featurefile.name, 1, tag_expr=tagexpressions.parse('good_case'))
            feature = parser.parse()
            feature.scenarios.should.have.length_of(2)

            # expect only bad case Scenarios parsed
            parser = FeatureParser(core, featurefile.name, 1, tag_expr=tagexpressions.parse('bad_case'))
            feature = parser.parse()
            feature.scenarios.should.have.length_of(1)

    def test_parse_feature_with_syntax_error(self):
        """
            Test parsing a feature which has syntax errors
        """
        feature = """
Bllllla: fooo
    @good_case
    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse.when.called.should.throw(FeatureFileSyntaxError)


    def test_parse_simple_background(self):
        """
        Test parsing a feature which has a simple background
        """
        feature = """
Feature: some feature
    Background: Some context
        Given I have a proper setup
        And I have a connection established

    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special

    Scenario: foo second it
        When I have a normal scenario
        Then I expect nothing special
"""
        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            feature = parser.parse()

            feature.background.shouldnt.be.none
            feature.scenarios.should.have.length_of(2)

            feature.background.all_steps.should.have.length_of(2)
            feature.background.all_steps[0].sentence.should.be.equal("Given I have a proper setup")
            feature.background.all_steps[1].sentence.should.be.equal("And I have a connection established")


    def test_parse_simple_background_with_subsequent_scenario_outline(self):
        """
        Test parsing a feature which has a simple background with a subsequent ScenarioOutline
        """
        feature = """
Feature: some feature
    Background: Some context
        Given I have a proper setup
        And I have a connection established

    Scenario Outline: foo
        When I have a normal scenario
        Then I expect nothing special

    Examples:
        | foo | bar |
        | 1   | 2   |

    Scenario: foo second it
        When I have a normal scenario
        Then I expect nothing special
"""
        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            feature = parser.parse()

            feature.background.shouldnt.be.none
            feature.scenarios.should.have.length_of(2)
            feature.scenarios[0].should.be.a(ScenarioOutline)


    def test_parse_simple_background_with_subsequent_scenario_loop(self):
        """
        Test parsing a feature which has a simple background with a subsequent ScenarioLoop
        """
        feature = """
Feature: some feature
    Background: Some context
        Given I have a proper setup
        And I have a connection established

    Scenario Loop 10: foo
        When I have a normal scenario
        Then I expect nothing special

    Scenario: foo second it
        When I have a normal scenario
        Then I expect nothing special
"""
        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            feature = parser.parse()

            feature.background.shouldnt.be.none
            feature.scenarios.should.have.length_of(2)
            feature.scenarios[0].should.be.a(ScenarioLoop)


    def test_parse_simple_background_with_subsequent_tag(self):
        """
        Test parsing a feature which has a simple background with a subsequent tag
        """
        feature = """
Feature: some feature
    Background: Some context
        Given I have a proper setup
        And I have a connection established

    @constant(foo: bar)
    @foo
    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special
"""
        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            feature = parser.parse()

            feature.background.shouldnt.be.none
            feature.scenarios.should.have.length_of(1)
            feature.scenarios[0].constants.should.have.length_of(1)
            feature.scenarios[0].tags.should.have.length_of(2)


    def test_parse_misplaced_background(self):
        """
        Test parsing a feature which has a misplaced background
        """
        feature = """
Feature: some feature
    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special

    Background: Some context
        Given I have a proper setup
        And I have a connection established
"""
        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse.when.called.should.throw(FeatureFileSyntaxError, "The Background block must be placed before any Scenario block")


    def test_parse_multiple_backgrounds(self):
        """
        Test parsing a feature which has a multiple backgrounds
        """
        feature = """
Feature: some feature
    Background: Some context
        Given I have a proper setup
        And I have a connection established

    Background: Some context 1
        Given I have a proper setup
        And I have a connection established

    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special
"""
        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse.when.called.should.throw(FeatureFileSyntaxError, "The Background block may only appear once in a Feature")
