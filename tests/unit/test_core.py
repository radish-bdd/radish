# -*- coding: utf-8 -*-


from unittest import TestCase


class ConfigurationTestCase(TestCase):
    """
        Tests for the runner class
    """
    def _makeOne(self, arguments):
        """
            return instance of class under test
        """
        from radish.core import Configuration
        return Configuration(arguments)

    def test_argument_name_transformation(self):
        """
            Test argument name transformation
        """

        test_arguments = {
            '--doubledash': '',
            '--with-dash': '',
            '<positional>': '',
            '<positional-with-dash>': '',
        }

        returned_config = self._makeOne(test_arguments)

        self.assertTrue(hasattr(returned_config, 'doubledash'))
        self.assertTrue(hasattr(returned_config, 'with_dash'))
        self.assertTrue(hasattr(returned_config, 'positional'))
        self.assertTrue(hasattr(returned_config, 'positional_with_dash'))

    def test_argument_value(self):
        """
            Test argument value setting
        """

        test_arguments = {
            '--argument': 'test_argument_value',
            '<positional-argument>': 'test_positional_argument_value',
        }

        returned_config = self._makeOne(test_arguments)

        self.assertTrue(returned_config.argument, 'test_argument_value')
        self.assertTrue(returned_config.positional_argument,
                        'test_positional_argument_value')
