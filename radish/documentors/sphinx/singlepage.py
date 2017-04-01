# -*- coding: utf-8 -*-

import os

from colorful import colorful

from radish.exceptions import RadishError
from radish.utils import console_write

from .document import SphinxDocument


# ........................................................................... #
class SinglePageSphinxBook(object):

    # ----------------------------------------------------------------------- #
    def __init__(self, file_path, label_prefix):
        self.file_path = file_path
        self.label_prefix = label_prefix
        self.document_class = SphinxDocument
        self._home_document = None

    # ----------------------------------------------------------------------- #
    def make_document(self):

        document_class = self.document_class
        # use the file path of the book
        document_file_path = document_class.make_file_name(self.file_path)

        # create instance of the document given passed in document class
        # give it document file path and and document label
        document = document_class(document_file_path, self.label_prefix)

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
        output = self._home_document.output()
        # return output, stripping any trailing whitespace/newlines
        return "%s\n" % output.rstrip()
