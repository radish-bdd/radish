# -*- coding: utf-8 -*-

import threading
import re

from tests.base import *

from radish.hookregistry import HookRegistry
from radish.feature import Feature
from radish.scenario import Scenario
from radish.stepmodel import Step
from radish.main import setup_config
import radish.utils as utils

# load extension
from radish.extensions.console_writer import ConsoleWriter
ConsoleWriter()

class ConsoleWriterTestCase(RadishTestCase):
    """
        Tests for the runner class
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
            "--with-traceback": False,
            "--marker": False,
            "--write-ids": False
        })

    def tearDown(self):
        """
            Overwrite because HookRegistry should not be reset
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
            Reset hook registry
        """
        HookRegistry().reset()

    def test_before_each_feature(self):
        """
            Test before.each_feature from extension console_writer
        """
        HookRegistry()
        data = threading.local()
        data.console = None

        def patched_write(text):
            text = re.sub(r"\x1b[^m]*m", "", text)
            data.console = text

        feature = Feature(1, "Feature", "Some feature", "somefile.feature", 1)

        with patch("radish.extensions.console_writer.write", side_effect=patched_write):
            HookRegistry().call("before", "each_feature", feature)

            data.console.should.be.equal("Feature: Some feature  # somefile.feature")

        feature.description.append("This is some description")
        feature.description.append("Because I want to test it")

        with patch("radish.extensions.console_writer.write", side_effect=patched_write):
            HookRegistry().call("before", "each_feature", feature)

            data.console.should.be.equal("""Feature: Some feature  # somefile.feature
    This is some description
    Because I want to test it""")

    def test_before_each_scenario(self):
        """
            Test before.each_scenario from extension console_writer
        """
        data = threading.local()
        data.console = None

        def patched_write(text):
            text = re.sub(r"\x1b[^m]*m", "", text)
            data.console = text

        scenario = Scenario(1, "Scenario", "Some scenario", "somefile.feature", 2, None)
        scenario.parent = Mock(spec=Feature)
        scenario.parent.id = 1
        scenario.parent.all_tags = []

        with patch("radish.extensions.console_writer.write", side_effect=patched_write):
            HookRegistry().call("before", "each_scenario", scenario)

            data.console.should.be.equal("\n    Scenario: Some scenario")

    def test_before_each_step(self):
        """
            Test before.each_step from extension console_writer
        """
        data = threading.local()
        data.console = None

        def patched_write(text):
            text = re.sub(r"\x1b[^m]*m", "", text)
            data.console = text

        scenario_mock = Mock()
        scenario_mock.id = 1
        scenario_mock.parent = None
        scenario_mock.all_tags = []
        step = Step(1, "I test the console writer", "somefile.feature", 3, scenario_mock, False)
        step.parent.parent = Mock(spec=Feature)
        step.parent.parent.id = 1
        step.parent.parent.all_tags = []

        with patch("radish.extensions.console_writer.write", side_effect=patched_write):
            HookRegistry().call("before", "each_step", step)

            data.console.should.be.equal("\r        I test the console writer")

    def test_after_each_step(self):
        """
            Test after.each_step from extension console_writer
        """
        data = threading.local()
        data.console = None

        def patched_write(text):
            text = re.sub(r"\x1b[^m]*m", "", text)
            data.console = text

        scenario_mock = Mock()
        scenario_mock.id = 1
        scenario_mock.parent = None
        scenario_mock.all_tags = []
        step = Step(1, "I test the console writer", "somefile.feature", 3, scenario_mock, False)
        step.parent.parent = Mock(spec=Feature)
        step.parent.parent.id = 1
        step.parent.parent.all_tags = []

        with patch("radish.extensions.console_writer.write", side_effect=patched_write):
            HookRegistry().call("after", "each_step", step)

            data.console.should.be.equal("\rI test the console writer")

    def test_after_each_step_failed(self):
        """
            Test after.each_step from extension console_writer with failed step
        """
        data = threading.local()
        data.console = None

        def patched_write(text):
            text = re.sub(r"\x1b[^m]*m", "", text)
            data.console = text

        scenario_mock = Mock()
        scenario_mock.parent = None
        step = Step(1, "I test the console writer", "somefile.feature", 3, scenario_mock, False)
        step.parent = MagicMock()
        step.parent.id = 1
        step.parent.parent = Mock(spec=Feature)
        step.parent.parent.id = 1
        step.state = step.State.FAILED
        try:
            assert False, "Some assertion happend"
        except AssertionError as e:
            step.failure = utils.Failure(e)

        with patch("radish.extensions.console_writer.write", side_effect=patched_write):
            HookRegistry().call("after", "each_step", step)

            data.console.should.be.equal("""\rI test the console writer
          AssertionError: Some assertion happend""")
