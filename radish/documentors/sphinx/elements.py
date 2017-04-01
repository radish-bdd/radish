# -*- coding: utf-8 -*-

import os


# ........................................................................... #
class TocTree(object):

    # ----------------------------------------------------------------------- #
    def __init__(self):
        # this mostly mirrors the behavior of the RST content tag
        self.caption = None
        self.maxdepth = 0
        self.documents = None

    # ----------------------------------------------------------------------- #
    def __str__(self):
        output = ""
        output += ".. toctree::\n"
        output += "    :maxdepth: %d\n" % self.maxdepth
        # set caption if exists
        if self.caption is not None:
            output += "    :caption: %s\n" % self.caption
        output += "\n"

        for document in self.documents:
            # strip off the ".rst" from the document_path
            rst_document_path = os.path.splitext(document.file_path)[0]
            output += "    %s\n" % rst_document_path

        return output
