# -*- coding: utf-8 -*-

import os

from radish.compat import string_types
from radish.documentors.utils import calculate_column_widths
from radish.documentors.utils import indent

from .elements import TocTree


# ........................................................................... #
class SphinxDocument(object):

    _HEADINGS = [
        "#", # 0
        "=", # 1
        "-", # 2
        "~", # 3
        "+", # 4
    ]

    # ----------------------------------------------------------------------- #
    def __init__(self, file_path, label_prefix):
        self.file_path = file_path
        self.label_prefix = label_prefix
        self._output_list = []
        self._first_header_set = False

        self._documents = []
        self._toctree = TocTree()

    # ----------------------------------------------------------------------- #
    def __repr__(self):
        return "<%s at %s : %s>" % \
            (self.__class__.__name__, hex(id(self)), self.file_path)

    # ----------------------------------------------------------------------- #
    @staticmethod
    def make_file_name(python_file_path):
        # split into list of (path/file_name, extension)
        document_file_path_list = list(os.path.splitext(python_file_path))
        # update the extension in the list to .rst
        document_file_path_list[1] = ".rst"
        # create document path
        document_file_path = "".join(document_file_path_list)

        return document_file_path

    # ----------------------------------------------------------------------- #
    @staticmethod
    def make_label_from_file_path(file_path, label_prefix):
        no_extention_path = os.path.splitext(file_path)[0]
        path_elements = no_extention_path.split(os.sep)
        label_path = ".".join(path_elements)
        label = "%s%s" % (label_prefix, label_path)
        return label

    # ----------------------------------------------------------------------- #
    def append(self, document):
        self._documents.append(document)

    # ----------------------------------------------------------------------- #
    def get_all_documents(self):
        docs = [self, ]
        for document in self._documents:
            docs.extend(document.get_all_documents())

        return docs

    # ----------------------------------------------------------------------- #
    def output(self):
        return "".join(map(str, self._output_list))

    # ----------------------------------------------------------------------- #
    def add_line(self, text):
        if isinstance(text, string_types):
            self._output_list.append("%s\n" % text)
        else:
            self._output_list.append(text)

    # ----------------------------------------------------------------------- #
    def add_linebreak(self):
        self.add_line("")

    # ----------------------------------------------------------------------- #
    def add_label(self, label):
        self.add_line(".. _%s:" % label)
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_comment(self, comment):
        # sphinx comment are very "invisible", they start with .. only
        # let's make this one visible
        prefixed_comment = "--- %s " % comment
        # shoudl pad to 79 but since we use 3 chares in the begining it's 76
        padded_comment = prefixed_comment.ljust(76, '-')
        self.add_line(".. %s" % padded_comment)
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_heading(self, text, level):
        # ~~~~~~~~~~~~~ #
        # create the ruler the length of the text
        ruler_char = self._HEADINGS[level]
        ruler = ruler_char * len(text)

        # ~~~~~~~~~~~~~ #
        # level ruler is "#" then the first
        if self._first_header_set is False:
            # this will only be raise during development of the docs
            # it should not happen during generation
            if level != 0:
                msg ="First heading of the Sphinx document should at level 0"
                raise ValueError(msg)
            # add overline ruler
            self.add_line(ruler)
            self._first_header_set = True

        # ~~~~~~~~~~~~~ #
        # add the text, the underline ruler and the line break
        self.add_line(text)
        self.add_line(ruler)
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_toctree(self, maxdepth, caption):
        self._toctree.maxdepth = maxdepth
        self._toctree.caption = caption
        self._toctree.documents = self._documents
        self.add_line(self._toctree)

    # ----------------------------------------------------------------------- #
    def add_contents(self, depth, caption):
        self.add_line(".. contents:: %s" % caption)
        self.add_line("    :depth: %d" % depth)
        self.add_line("    :local:")
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_ruler(self):
        ruler = "-" * 79
        self.add_linebreak()
        self.add_line(ruler)
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_table(self, data, headers=None, alignment=None):

        # if alignment is not passed in then create a default alignment to the
        # "left".  number of columns in the first data row is used to create
        # the tuple with alignment
        if alignment is None:
            alignment = ("left",) * len(data[0])

        alignment_map = {
            "left": str.ljust,
            "right": str.rjust,
            "center": str.center,
        }

        # form a two dimmensional array from data rows and header if header
        # were given
        # [
        #   ("header one"       , "header 2"   , "header3"        ),
        #   ( "a"               , "river flows", "7"              ),
        #   ( "they"            , "said"       , "I am super nice"),
        #   ( "once upon a time", "a"          , "princes"        ),
        # ]
        # make copy of the data list so we do not modify the exiting one
        all_rows = data[:]
        if headers is not None:
            all_rows.insert(0, headers)

        # get the column widths
        column_widths = calculate_column_widths(all_rows)

        # generate table border line using the column widths
        border_row = ("=" * width for width in column_widths)
        # make border row tuple into rst border text
        border_text = " ".join(border_row)

        # go over each row and cell in all_rows and align/padd each to the
        # value of that column in alignment using spaces
        rst_table = []
        for row in all_rows:
            prepped_row = []
            prepped_row_text = None
            for column_index, text in enumerate(row):
                # get the left/right/center string
                align_style = alignment[column_index]
                # get the function corresponding to align_style from
                # alignment_map
                align_func = alignment_map[align_style]
                # get the column_width for this column
                width = column_widths[column_index]
                # get the aligned text
                aligned_text = align_func(text, width)
                # add the aligned_text to as column in the prepped_row
                prepped_row.append(aligned_text)
                # generate row text
                prepped_row_text = " ".join(prepped_row)

            # add the prepped row text to the table if it has been filled out
            if prepped_row_text is not None:
                rst_table.append(prepped_row_text)

        # add table top border as the top row
        rst_table.insert(0, border_text)

        # if headers were passed in then  all_rows = header + rows and
        # current first row in the rst_table is the header row. so we need to
        # put a border row after it (3rd row)
        if headers is not None:
            rst_table.insert(2, border_text)

        # append the border to the bottom of the table
        rst_table.append(border_text)
        # create rst table text by combining each row with newline separator
        rst_table_text = "\n".join(rst_table)
        # write tst table to the document (with additional newline)
        self.add_line(rst_table_text)
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_field_list(self, table):
        for name, text in table:
            self.add_line(":%s: %s" % (name, text))
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_index(self, entry):
        # start index
        index_entry = ".. index:: %s" % entry
        self.add_line(index_entry)
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_indices(self, indices):
        # start index
        self.add_line(".. index::")
        # add index entry and sub entry as a "single" entry
        for entry, sub_entry in indices:
            self.add_line("    single: %s; %s" % (entry, sub_entry))
        # add empty new line
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_indented_paragraph(self, text):
        self.add_linebreak()
        self.add_line(indent(text, 2))
        self.add_linebreak()

    # ----------------------------------------------------------------------- #
    def add_todo(self, text):
        self.add_linebreak()
        # start index
        self.add_line(".. todo::")
        # create indented todo text line
        indented_text = "    %s" % text
        self.add_line(indented_text)
        # add empty new line
        self.add_linebreak()
