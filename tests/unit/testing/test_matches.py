# -*- coding: utf-8 -*-

import os
import re
import tempfile

from tests.base import *

import radish.testing.matches as matches


class MatchesTestCase(RadishTestCase):
    """
    Unit tests for testing.matches module.
    """
    def test_unreasonable_min_coverage(self):
        """
        Test unreasonable minimum test coverage
        """
        matches.test_step_matches_configs.when.called_with(None, [], 101).should.return_value(3)

    def test_no_steps_found(self):
        """
        Test if basedir does not contain any steps to test against
        """
        with patch('radish.testing.matches.load_modules'):
            matches.test_step_matches_configs.when.called_with(None, []).should.return_value(4)


    def test_empty_matches_config(self):
        """
        Test empty matches config file
        """
        # create temporary file
        fd, tmpfile = tempfile.mkstemp()
        os.close(fd)

        with patch('radish.testing.matches.load_modules'), patch('radish.testing.matches.StepRegistry.steps') as steps_mock:
            steps_mock.return_value = [1, 2]
            matches.test_step_matches_configs.when.called_with([tmpfile], []).should.return_value(5)

        # delete temporary file
        os.remove(tmpfile)

    def test_step_matches_invalid_match_config(self):
        """
        Test match config without a sentence and a should_match attribute
        """
        # test config with missing should_match function attribute
        config = [{
            'sentence': None
        }]

        matches.test_step_matches.when.called_with(config, []).should.throw(ValueError,
            'You have to provide a sentence and the function name which should be matched (should_match)')  # pylint: disable=bad-continuation


        # test config with missing sentence attribute
        config = [{
            'should_match': None
        }]

        matches.test_step_matches.when.called_with(config, []).should.throw(ValueError,
            'You have to provide a sentence and the function name which should be matched (should_match)')  # pylint: disable=bad-continuation


        # test empty config
        config = [{}]

        matches.test_step_matches.when.called_with(config, []).should.throw(ValueError,
            'You have to provide a sentence and the function name which should be matched (should_match)')  # pylint: disable=bad-continuation

    def test_sentence_no_step_match(self):
        """
        Test if sentence does not match any step pattern
        """
        steps = {}
        config = [{
            'sentence': 'foo', 'should_match': 'bar'
        }]

        with patch('sys.stdout', new=StringIO()) as out:
            matches.test_step_matches.when.called_with(config, steps).should.return_value((1, 0))
            out.seek(0)
            out.read().should.contain('Expected sentence didn\'t match any step implemention')

    def test_sentence_match_wrong_step(self):
        """
        Test if sentence matched wrong step
        """
        def foo():
            "Test step func"
            pass


        steps = {
            re.compile('foo'): foo
        }
        config = [{
            'sentence': 'foo', 'should_match': 'bar'
        }]

        with patch('sys.stdout', new=StringIO()) as out:
            matches.test_step_matches.when.called_with(config, steps).should.return_value((1, 0))
            out.seek(0)
            out.read().should.contain('Expected sentence matched foo instead of bar')

    def test_sentence_argument_errors(self):
        """
        Test if sentence arguments do not match
        """
        def foo(step, foo, bar):
            "Test step func"
            pass


        steps = {
            re.compile(r'What (.*?) can (.*)'): foo
        }
        config = [{
            'sentence': 'What FOO can BAR', 'should_match': 'foo',
            'with-arguments': [
                {'foo': 'foooooooo'},
                {'bar': 'baaaaaaar'}
            ]
        }]

        with patch('sys.stdout', new=StringIO()) as out:
            matches.test_step_matches.when.called_with(config, steps).should.return_value((1, 0))
            out.seek(0)
            output = out.read()
            output.should.contain('Expected argument "foo" with value "foooooooo" does not match value "FOO"')
            output.should.contain('Expected argument "bar" with value "baaaaaaar" does not match value "BAR"')

    def test_sentence_step_arguments_no_corresponding(self):
        """
        Test sentence step arguments without corresponding actual argument
        """
        expected_arguments = {
            'foo': 'fooo'
        }

        actual_arguments = {
            'FOO': None
        }

        matches.check_step_arguments.when.called_with(expected_arguments, actual_arguments).should.return_value([
            'Expected argument "foo" is not in matched arguments [\'FOO\']'])

    def test_sentence_step_arguments_type_mismatch(self):
        """
        Test sentence step arguments with type mismatch
        """
        expected_arguments = {
            'foo': 'fooo'
        }

        actual_arguments = {
            'foo': 42
        }

        matches.check_step_arguments.when.called_with(expected_arguments, actual_arguments).should.return_value([
            'Expected argument "foo" is of type "int" instead "str"'])

    def test_sentence_step_arguments_value_mismatch(self):
        """
        Test sentence step arguments with value mismatch
        """
        expected_arguments = {
            'foo': 'fooo'
        }

        actual_arguments = {
            'foo': 'foo'
        }

        matches.check_step_arguments.when.called_with(expected_arguments, actual_arguments).should.return_value([
            'Expected argument "foo" with value "fooo" does not match value "foo"'])

    def test_sentence_step_arguments_match(self):
        """
        Test sentence step arguments match
        """
        expected_arguments = {
            'foo': 'foo',
            'bar': 'bar'
        }

        actual_arguments = {
            'foo': 'foo',
            'bar': 'bar'
        }

        matches.check_step_arguments.when.called_with(expected_arguments, actual_arguments).should.return_value([])
