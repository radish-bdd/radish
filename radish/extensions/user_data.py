# -*- coding: utf-8 -*-

"""
This module provides a hook which processes user specified data on the command-line
and provides this data as a dictionary attached to the world.config object
as per Enhancement #124.
"""
import re

from radish.terrain import world
from radish.exceptions import RadishError
from radish.extensionregistry import extension


@extension
class UserData(object):
    """
    User Data radish extension
    """

    OPTIONS = [
        (
            "-u=<userdata> | --user-data=<userdata>...",
            "User data as 'key=value' pair. You can specify --user-data multiple times.",
        )
    ]
    LOAD_IF = staticmethod(lambda config: True)
    LOAD_PRIORITY = (
        2
    )  # This should probably load early in-case another extension needs to inspect this data.

    def __init__(self):
        self._kv_regex = re.compile(r"\s*=\s*")

        self._cli_user_data = world.config.user_data  # Save the data to process later
        world.config.user_data = {}  # Initialize user data dictionary

        self.process_user_data()

    def process_user_data(self):
        """
        Process the user data
        """
        if self._cli_user_data:
            for pair in self._cli_user_data:
                try:
                    key, value = map(str.strip, self._kv_regex.split(pair, maxsplit=1))
                except ValueError as e:
                    msg = "-u/--user-data: User data is invalid. Expecting: 'key=value' Got: '{0}'"
                    raise RadishError(msg.format(pair))

                # Allowing all keys and values, even if empty
                world.config.user_data[key] = value
