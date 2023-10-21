# -*- coding: utf-8 -*-

"""
    This module provides a registry for all hooks
"""

from singleton import singleton
from rich.console import Console
from rich.live import Live
from radish import world

ANSI_LINE_JUMP_SEQUENCE = "\r\033[A\033[K" 


@singleton()
class Printer(object):
    """
    Represents an object with all registered hooks
    """


    def __init__(self):
        self.out_file = None
        self.style_on = True
        self._init_consoles()
        self.lines = []
        
    def clear(self):
        self.lines = []
        self.live.update(self.get_console_text())
        
    def _init_consoles(self):
        self.console = Console(file=self.out_file)
        self.live = Live(self.console)
        
    def set_style_on(self, on: bool):
        self.style_on = on
    
    def out_to_file(self, file):
        self.out_file = file
        self._init_consoles()
        
    def get_console_text(self):
        return '\n'.join(self.lines)
    
    def write(self, text, end="\n"):
        # rich does not support the ansi line skip sequence
        # and making gherkin use rich's live data stuff turned out
        # to be pretty challanging

        # so this is a work around to print the line jumps like normal
        # then remove them from the pretty string
        line_jumps = text.count(ANSI_LINE_JUMP_SEQUENCE)
        text = text.replace(ANSI_LINE_JUMP_SEQUENCE, "")
        for _ in range(line_jumps):
            self.lines.pop()
        self.lines.append(text)
        self.live.update(self.get_console_text())
            
            
            
    
def styled_text(text, style):
    """
    inject the style into the text if not ansi and
    if style not disabled

    :param str text: the text which is printed to the console
    :param str style: the style to inject.
    for reference: https://rich.readthedocs.io/en/latest/style.html
    """
    if world.config.no_ansi or not Printer().style_on:
        return text
    else:
        return f"[{style}]{text}[/{style}]"