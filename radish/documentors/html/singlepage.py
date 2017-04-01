# -*- coding: utf-8 -*-

import os

from colorful import colorful

from radish.exceptions import RadishError
from radish.utils import console_write

from .document import HtmlDocument
from .elements import TocTree

# ........................................................................... #
class SinglePageHtmlBook(object):

    # ----------------------------------------------------------------------- #
    def __init__(self, file_path):
        self.file_path = file_path
        self.label_prefix = ''
        self.document_class = HtmlDocument
        self._home_document = []

    # ----------------------------------------------------------------------- #
    @property
    def toctree(self):
        toctree_ = TocTree()
        toctree_.set_documents([self._home_document, ])
        # do not set depth_uri, that will be passed in by each document
        # so the generated url is specific to it
        return toctree_

    # ----------------------------------------------------------------------- #
    def make_document(self):
        document_class = self.document_class
        # use the file path of the book
        document_file_path = document_class.make_file_name(self.file_path)

        # create instance of the document given passed in document class
        # give it document file path and and document label
        document = document_class(document_file_path)

        return document

    # ----------------------------------------------------------------------- #
    def set_home_document(self, document):
        self._home_document = document

    # ----------------------------------------------------------------------- #
    def print_to_console(self):
        print(self._output())

    # ----------------------------------------------------------------------- #
    def write_file(self, file_path, overwrite):

        if os.path.isfile(file_path) is True and overwrite is False:
            msg = "output file already exists: %s" % file_path
            raise RadishError(msg)

        # open file
        file_handle = open(file_path, mode="w")
        # write documents output content to the file
        file_handle.write(self._output())
        # close file
        file_handle.close()
        # write out success to console
        status_text = colorful.bold_white("writing output: ")
        status_text += colorful.green(file_path)
        console_write(status_text)

    # ----------------------------------------------------------------------- #
    def _output(self):
        output = self._home_document.output(self.toctree)

        # return output, stripping any trailing whitespace/newlines
        return "%s\n" % output.rstrip()
