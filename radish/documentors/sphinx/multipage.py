# -*- coding: utf-8 -*-

import os
import shutil

from colorful import colorful

from radish.exceptions import RadishError
from radish.utils import console_write
from radish.utils import expandpath

from .document import SphinxDocument


# ........................................................................... #
class MultiPageSphinxBook(object):

    # ----------------------------------------------------------------------- #
    def __init__(self, home_file_path, label_prefix):
        self.home_file_path = home_file_path
        self.title = None
        self.label_prefix = label_prefix
        self.document_class = SphinxDocument
        self._home_document = None

    # ----------------------------------------------------------------------- #
    def make_document(self, file_path):
        document_class = self.document_class
        # passed in path
        document_file_path = document_class.make_file_name(file_path)

        # make label for this document from the file path and prefix
        # create instance of the document given passed in document class
        # give it document file path and and document label
        document = document_class(document_file_path, self.label_prefix)

        return document

    # ----------------------------------------------------------------------- #
    def set_home_document(self, document):
        self._home_document = document

    # ----------------------------------------------------------------------- #
    def get_all_documents(self):
        return self._home_document.get_all_documents()

    # ----------------------------------------------------------------------- #
    def write_files(self, output_folder, overwrite):

# TODO: do not use expand path cause $PWD should not be given
        real_output_folder = expandpath(output_folder)

        # ~~~~~~~~~~~~~~~~~~~~ #
        # if the output folder exists (could be folder, filer, etc)
        if os.path.exists(real_output_folder) is True:
            # if overwrite option is true then remove the existing folder.
            if overwrite is True:
                shutil.rmtree(real_output_folder)
            else:
                # other wise raise a RadishError with output folder
                msg = "output folder already exists: %s" % real_output_folder
                raise RadishError(msg)

        # create the output folder
        os.makedirs(real_output_folder)

        # ~~~~~~~~~~~~~~~~~~~~ #
        # go over all the documents and write output f
        for document in self.get_all_documents():

            # ~~~~~~~~~~~~~~~~~~~~ #
            # create the output file path from the output folder
            output_file_path = os.path.join(real_output_folder,
                                            document.file_path)
            # get the folder the file will be in
            output_file_folder = os.path.dirname(output_file_path)

            # if that folder does not exist yet, create it
            if os.path.isdir(output_file_folder) is False:
                os.makedirs(output_file_folder)

            # ~~~~~~~~~~~~~~~~~~~~ #
            # open file the document will be written to
            file_handle = open(output_file_path, mode="w")
            # write documents output content to the file
            file_handle.write(document.output())
            # close file
            file_handle.close()

            # ~~~~~~~~~~~~~~~~~~~~ #
            # write out success to console
            status_text = colorful.bold_white("writing output: ")
            status_text += colorful.green(output_file_path)
            console_write(status_text)
