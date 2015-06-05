# -*- coding: utf-8 -*-

import threading
import re

from tests.base import *

import radish.extensions.console_writer
from radish.hookregistry import HookRegistry
from radish.feature import Feature
from radish.scenario import Scenario
from radish.step import Step


class ConsoleWriterTestCase(RadishTestCase):
    """
        Tests for the runner class
    """
    def tearDown(self):
        """
            Overwrite because HookRegistry should not be reset
        """
        pass

    @classmethod
    def tearDownClass(self):
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

            data.console.should.be.equal("Feature: Some feature")

        feature.description.append("This is some description")
        feature.description.append("Because I want to test it")

        with patch("radish.extensions.console_writer.write", side_effect=patched_write):
            HookRegistry().call("before", "each_feature", feature)

            data.console.should.be.equal("""Feature: Some feature
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
        scenario_mock.parent = None
        step = Step(1, "I test the console writer", "somefile.feature", 3, scenario_mock, False)

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
        scenario_mock.parent = None
        step = Step(1, "I test the console writer", "somefile.feature", 3, scenario_mock, False)

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
        step.state = step.State.FAILED
        try:
            assert False, "Some assertion happend"
        except AssertionError, e:
            step.failure = step.Failure(e)

        with patch("radish.extensions.console_writer.write", side_effect=patched_write):
            HookRegistry().call("after", "each_step", step)

            data.console.should.be.equal("""\rI test the console writer
          AssertionError: Some assertion happend""")
