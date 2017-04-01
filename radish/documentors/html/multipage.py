# -*- coding: utf-8 -*-

import os
import shutil

from colorful import colorful

from radish.exceptions import RadishError
from radish.utils import console_write
from radish.utils import expandpath

from .document import HtmlDocument
from .elements import TocTree

# ........................................................................... #
class MultiPageHtmlBook(object):

    # ----------------------------------------------------------------------- #
    def __init__(self, home_file_path):
        self.home_file_path = home_file_path
        self.title = None
# TODO: there is no label prefix for HTML but the writer still needs it.
#       try to change it to the book call reference
        self.label_prefix = ''
        self.document_class = HtmlDocument
        self._home_document = None

    # ----------------------------------------------------------------------- #
    def __repr__(self):
        return "<%s at %s : '%s'>" % \
            (self.__class__.__name__, hex(id(self)), self.title)

    # ----------------------------------------------------------------------- #
    @property
    def toctree(self):
        toctree_ = TocTree()
        toctree_.set_documents([self._home_document, ])
        # do not set depth_uri, that will be passed in by each document
        # so the generated url is specific to it
        return toctree_


    # ----------------------------------------------------------------------- #
    def make_document(self, file_path):
        document_class = self.document_class
        # passed in path
        document_file_path = document_class.make_file_name(file_path)

        # make label for this document from the file path and prefix
        # create instance of the document given passed in document class
        # give it document file path and and document label
        document = document_class(document_file_path)

        return document

    # ----------------------------------------------------------------------- #
    def set_home_document(self, document):
        self._home_document = document

    # ----------------------------------------------------------------------- #
    def get_all_documents_with_trails(self):
        return self._home_document.get_all_documents_with_trails([self,])

    # ----------------------------------------------------------------------- #
    @property
    def file_path(self):
        # provide file_path because it is used to resolve crumbs to the "top"
        # of the book, which of course is the home document
        return self._home_document.file_path

    # ----------------------------------------------------------------------- #
    def make_crumb(self, depth_uri):
        # use the title from the book and the url from home document
        return (self.title, self._home_document.make_crumb(depth_uri)[1])

    # ----------------------------------------------------------------------- #
    def write_files(self, output_folder, overwrite):

        # ~~~~~~~~~~~~~~~~~~~~ #
        # get all the documents with trails
        documents_with_trails = self.get_all_documents_with_trails()

        # ~~~~~~~~~~~~~~~~~~~~ #
        # create document sequence used for previous/next navigation
        # first create list of all actual documents which are the last element
        # in each list entry of documents with trails
        document_sequence = list(document_trail[-1] for \
                                    document_trail in documents_with_trails)
        # if the sequence exists then add None to the front and end of
        # the sequence. they will indicate that the first and last document
        # have no previous and next
        if len(document_sequence) > 0:
            document_sequence.insert(0, None)
            document_sequence.append(None)

        # ~~~~~~~~~~~~~~~~~~~~ #
# TODO: do not use expand path cause $PWD should not be given
        real_output_folder = expandpath(output_folder)
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
        # go over all the document trails and generate output for each
        # document element of the trail including with crumbs and previous/next
        # elements
        # note: enumerate is used so we can get previous/next from
        #       document_sequence using index from the iteration.
        #       the enumerate sequence starts at 1 because we prepended None
        #       as the first element of the document_sequence so it would
        #       indicate, that the "previous" element of the first document
        #       does not exist
        for index, document_trail in enumerate(documents_with_trails,1):

            # ~~~~~~~~~~~~~~~~~~~~ #
            # get the actual document we need to output from the trail which
            # is the last element
            document = document_trail[-1]

            # ~~~~~~~~~~~~~~~~~~~~ #
            # get the breadcrumb document (everything but the last element)
            crumb_documents = document_trail[:-1]
            # make a tuple of crumbs by calling each crumb document
            # "make_crumb" function and giving it the the path to the the
            # documentent we are outputing. It's path will then be used to
            # generate "../../" style path
            # for example:
            #   when document.file_path of "foo/bar/hello.rst" is given
            #   to the make_crumb function of each document the path of
            #   "../../hello.rst" is created since the original path is
            #   two folders down. basically the path is absolute to the top

            crumbs = tuple(crumb_document.make_crumb(document.depth_uri) \
                               for crumb_document in crumb_documents)

            # ~~~~~~~~~~~~~~~~~~~~ #
            # get the previous and next document using document_sequence
            # elements at index - 1 for previous document and index + 1 for
            # next document. This works for all documents since the sequence
            # is 2 element larger with None prepended to the beginning and
            # as well as appended to the end.
            # note: remember index starts at 1
            previous_document = document_sequence[index - 1]
            if previous_document is not None:
                previous_crumb = \
                    previous_document.make_crumb(document.depth_uri)
            else:
                previous_crumb = None

            next_document = document_sequence[index + 1]
            if next_document is not None:
                next_crumb = next_document.make_crumb(document.depth_uri)
            else:
                next_crumb = None


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
            # generate document content
            output = document.output(self.toctree, crumbs, previous_crumb,
                                     next_crumb)
            # open file the document will be written to
            file_handle = open(output_file_path, mode ="w")
            # write documents output content to the file
            file_handle.write(output)
            # close file
            file_handle.close()

            # ~~~~~~~~~~~~~~~~~~~~ #
            # write out success to console
            status_text = colorful.bold_white("writing output: ")
            status_text += colorful.green(output_file_path)
            console_write(status_text)
