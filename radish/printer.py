# -*- coding: utf-8 -*-

"""
    This module provides an interface to work with the Rich library.
    
"""

from typing import IO
from singleton import singleton
from rich.console import Console
from rich.live import Live
from radish import world


# The ansi line jump sequence will remove a line from the output
ANSI_LINE_JUMP_SEQUENCE = "\r\033[A\033[K"


@singleton()
class Printer(object):
    """
    An object responsible for maintaining the rich Live session
    and any settings. It is a singleton because a single live session
    is allowed to be active at one time, otherwise an exception will
    be raised.
    """

    def __init__(self):
        self.out_file = None
        self.width = None
        self.height = None
        self.style_on = True
        self.is_live = True
        self._init_consoles()
        self.lines = []

    def clear(self):
        """
        Clear the cached lines and update the live display. This is required to
        clear the data of the singleton between tests.
        """
        self.lines = []
        self.live.update(self._build_live_text())

    def _init_consoles(self):
        """
        Recreate console and live session with current settings.
        """
        self.console = Console(file=self.out_file, width=self.width, height=self.height, soft_wrap=True)
        self.live = Live(self.console)

    def set_live(self, on: bool):
        """Toggle live status, if live status is off, then
        printing will go directly to the console. This is required
        to retrieve the output for tests as a live session.

        Args:
            on (bool): live is on(True) of off(False)
        """
        self.is_live = on

    def set_style_on(self, on: bool):
        """Turn style on or off

        Args:
            on (bool): style on(True) or off(False)
        """
        self.style_on = on

    def out_to_file(self, file: IO[str]):
        """Set the out destination of the console

        Args:
            file (File): the write file or destination
        """
        self.out_file = file
        self._init_consoles()

    def set_size(self, width: int, height: int):
        """Set the size of the console, Rich does this by default
        based on environment variables, but for tests, this is
        required for consistency

        Args:
            width (int): width of console
            height (int): height of console
        """
        self.width = width
        self.height = height
        self._init_consoles()

    def _build_live_text(self) -> str:
        return "\n".join(self.lines)

    def get_console_output(self):
        return self.console.file.getvalue()

    def write(self, text: str):
        """Write to the live session OR directly to the console, support
        existing line-replace mechanism by removing a line for each time the
        line jump sequence appears in the text. Then append the new text to
        existing lines and update the live display.

        Args:
            text (str): The new text to add.
        """
        if self.is_live:
            line_jumps = text.count(ANSI_LINE_JUMP_SEQUENCE)
            text = text.replace(ANSI_LINE_JUMP_SEQUENCE, "")
            for _ in range(line_jumps):
                if len(self.lines):
                    self.lines.pop()
            self.lines.append(text)
            self.live.update(self._build_live_text())
        else:
            self.console.print(text)


def styled_text(text, style):
    """
    inject the style into the text if not ansi and
    if style not disabled

    :param str text: the text which is printed to the console
    :param str style: the style to inject.
    for reference: https://rich.readthedocs.io/en/latest/style.html
    """
    if world.config.no_ansi or not printer.style_on:
        return text
    else:
        return f"[{style}]{text}[/{style}]"


printer = Printer()
