# -*- coding: utf-8 -*-

import inspect
import os

from collections import OrderedDict

from radish.exceptions import RadishError
from radish.utils import expandpath

from .elements import StepDefintionModule
from .elements import StepDefinition


# ........................................................................... #
class StepsMultiPageWriter(object):

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
        # set the book title
        book.title = "Radish"
        # generate home document and set it as the home document of the book
        home_document = self._make_home_document(book)
        book.set_home_document(home_document)

        # go over all the step defintion modules
        for module in modules.values():
            document = self.make_document(book, module.relative_file_path)
            # write step definition module documentation to the module
            module.write_to(document, heading_level=0, with_contents=True)
            # the written document to the book
            home_document.append(document)

    # ----------------------------------------------------------------------- #
    def make_document(self, book, relative_file_path):
        document = book.make_document(relative_file_path)
        return document

    # ----------------------------------------------------------------------- #
    def _make_home_document(self, book):

        # make home document using the index file path in the book
        document = book.make_document(book.home_file_path)

        # ~~~~~~~~~~~~~~~~ #
        # add a commment with file_path in it
        document.add_comment(document.file_path)

        # ~~~~~~~~~~~~~~~~ #
        # add label
        document_class = book.document_class
        label = document_class.make_label_from_file_path(document.file_path,
                                                         book.label_prefix)
        document.add_label(label)

        # ~~~~~~~~~~~~~~~~ #
        # add book title as step modules heading
        document.add_heading("Step Modules", 0)
        document.add_line("The following step definitions are provided here.")
        document.add_ruler()

        # ~~~~~~~~~~~~~~~~ #
        # add table of contents
        document.add_toctree(maxdepth=3, caption="Contents")

        return document

