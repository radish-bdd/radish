# -*- coding: utf-8 -*-

import inspect

from collections import OrderedDict

from radish.exceptions import RadishError
from radish.utils import expandpath

from .elements import StepDefinition
from .elements import StepDefintionModule


# ........................................................................... #
class StepsSinglePageWriter(object):

    # ----------------------------------------------------------------------- #
    def __init__(self, steps, basedir):
        self._basedir = expandpath(basedir)
        self._steps = steps

    # ----------------------------------------------------------------------- #
    def write_to(self, book):

        # ~~~~~~~~~~~~~~~~~~~~~~~ #
        # if there are no steps, do not generate anything
        if len(self._steps) == 0:
            raise RadishError("No Step Definitions found.")

        modules = OrderedDict()

        # ~~~~~~~~~~~~~~~~~~~~~~~ #
        # go over all the steps, create StepDefintion for each step and add
        # each step to the key dictionary for it's file. In short this creates
        # a collection of steps assigned to each file they belong to
        for pattern, callable_ in self._steps.items():
            # python filename of the callable for the step definition
            file_path = inspect.getfile(callable_)
            # create step defintion
            step_definition = StepDefinition(pattern, callable_)

            # if we already created the step defintion module for this file
            # path then get it from modules
            if file_path in modules:
                module = modules[file_path]
            else:
                # create step defintion module
                module = StepDefintionModule(file_path, self._basedir)

            # now add this step defintion to this module since it defined in it
            module.add(step_definition)
            modules[file_path] = module

        # ~~~~~~~~~~~~~~~~~~~~~~~ #
        # create the document
        document = self.make_document(book)

        # ~~~~~~~~~~~~~~~~~~~~~~~ #
        self._write_home_section(document)

        # ~~~~~~~~~~~~~~~~~~~~~~~ #
        # go over all the step defintion modules
        for module in modules.values():
            # write step definition module documentation to the module
            module.write_to(document, heading_level=1, with_contents=False)
            # add line break for more human readability for each module
            document.add_linebreak()

        # set document as the home document of the book (only document really)
        book.set_home_document(document)

    # ----------------------------------------------------------------------- #
    def make_document(self, book):
        document = book.make_document()
        return document

    # ----------------------------------------------------------------------- #
    def _write_home_section(self, document):

        # ~~~~~~~~~~~~~~~~ #
        # add a commment with file_path in it
        document.add_comment(document.file_path)

        # ~~~~~~~~~~~~~~~~ #
        # add label
        label = document.make_label_from_file_path(document.file_path,
                                                   document.label_prefix)
        document.add_label(label)

        # ~~~~~~~~~~~~~~~~ #
        # add document heading
        document.add_heading("Step Modules", 0)
        document.add_line("The following step definitions are provided here.")
        document.add_ruler()

        # ~~~~~~~~~~~~~~~~ #
        # add table of contents
        document.add_contents(depth=3, caption="Contents")

        return document
