# -*- coding: utf-8 -*-

import re
import os

from collections import OrderedDict
from textwrap import dedent

from radish.compat import pathname2url
from radish.compat import string_types

from radish.documentors.utils import calculate_column_widths
from radish.documentors.utils import indent
from radish.documentors.utils import strip_leading_whitespace

from .elements import Contents
from .elements import TocTree

from .utils import make_depth_uri
from .utils import make_id
from .utils import make_parent_uri
from .utils import safe_url_join

# ........................................................................... #
class HtmlDocument(object):

    _HEADINGS = [
        "h1", # 0
        "h2", # 1
        "h3", # 2
        "h4", # 3
        "h5", # 4
    ]

    # ----------------------------------------------------------------------- #
    def __init__(self, file_path):
        self.file_path = file_path
        self.label_prefix = ''
        self.title = None

        # create the uri out of the file path
        self.uri = pathname2url(file_path)
        # uri of the parent folder
        self.parent_uri = make_parent_uri(file_path)
        # depth uri require to walk to the top
        self.depth_uri = make_depth_uri(file_path)

        self.contents = Contents()
# TODO: this need to be public
        self._documents = []

        self._labels = OrderedDict()
        self._toctree = TocTree()
        self._output_list = []

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
        document_file_path_list[1] = ".html"
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

    # ----------------------------  ----------------------------------------- #
    def append(self, document):
        self._documents.append(document)

    # ----------------------------------------------------------------------- #
    def make_crumb(self, depth_uri):
        relative_uri = safe_url_join(depth_uri, self.uri)
        return self.title, relative_uri


    # ----------------------------------------------------------------------- #
    def get_all_documents_with_trails(self, parents):
        docs = [parents + [self, ]]
        for document in self._documents:
            current_trail = parents + [self, ]
            docs.extend(document.get_all_documents_with_trails(current_trail))

        return docs

    # ----------------------------------------------------------------------- #
    def _crumbs(self, crumbs):
        output = ""

        # start the breadcrubs
#        output += '<br />\n'
        output += '<ol class="breadcrumb radish-breadcrumb">\n'

        # go over breadcrumb text and targets and add them as links
        for text, target in crumbs:
            output += '  <li><a href="%s">%s</a></li>\n' % (target, text)

        # add text (but no link) for this document
        output += '  <li class="active">%s</li>\n' % self.title
        # close the breadcrumbs
        output += '</ol>'

        return output

    # ----------------------------------------------------------------------- #
    def _nav_links(self, previous_crumb, next_crumb, reverse=False):

        output = ''
        links = ''
        headers = ''

        if previous_crumb is None and next_crumb is None:
            return ''
        else:
            # text headers with title/first heading of the next file
            headers += '<div class="clearfix">\n'
            # link to the next file
            links += '<div class="clearfix">\n'

            if previous_crumb is not None:
                headers += '<small class="text-muted pull-left">%s</small>\n' \
                              % previous_crumb[0]
                links += '<a class="pull-left" href="%s">&laquo; Previous</a>\n' \
                              % previous_crumb[1]

            if next_crumb is not None:
                headers += '<small class="text-muted pull-right">%s</small>\n' \
                              % next_crumb[0]
                links += '<a class="pull-right" href="%s">Next &raquo;</a>\n' \
                              % next_crumb[1]

            links += '</div>\n'
            headers += '</div>\n'

            if reverse is True:
                output = links + headers
            else:
                output = headers + links

        return output

    # ----------------------------------------------------------------------- #
    def output(self, toctree, crumbs=None, previous_crumb=None, next_crumb=None):

        # ~~~~~~~~~~~~~~~~~~~ #
        html_source = dedent("""\
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset='utf-8'>
            <meta http-equiv='X-UA-Compatible' content='IE=edge'>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
            <title>%(title)s - Radish Documentation</title>
            <link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css' integrity='sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u' crossorigin='anonymous'>
            <!-- Optional theme -->
            <link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css' integrity='sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp' crossorigin='anonymous'>
            <style type='text/css'>
              /* add padding to the bottom of the body, since visually it is
                 helpful have some extra whitespace */
              body {
                padding-bottom: 50px;
              }

              /* for some reason the last row is too high in bootstrap, so
                 remove the bottom margin on the table */
              table {
                margin-bottom: 0px !important; */
              }

              /* style for radish sidebar */
              .radish-sidebar {
                  position: fixed;
                  float: left;
                  margin-left: 0;
                  width: 300px;
                  height: 100%%;
                  overflow-wrap: break-word;
                  overflow-y: auto;
                  z-index: 200;
                  border-right: 1px dotted black;
                  font-size: 14px;
                  line-height: 1.5;
                  word-wrap: break-word;
              }

              .radish-sidebar ul, .radish-sidebar li {
                list-style-type: none;
                padding: 0;
                margin: 0;
              }

              .radish-sidebar li {
                padding-left: 16px;
              }

              .radish-sidebar-header {
                margin-top: 10px;
                margin-bottom: 10px;
                padding-bottom: 10px;
                padding-left: 0;
                border-bottom: 1px dotted black;
              }

              .radish-container {
                padding-left: 0;
              }

              /* style for radish content with respect to the sidebar */
              .radish-content {
                  margin: 0 0 0 320px;
                  max-width: 800px;
              }

              a.headerlink {
                  color: #DDD;
                  padding: 0 4px;
                  text-decoration: none;
                  font-size: 40%%;
                  vertical-align: middle;
              }

              a.headerlink:hover {
                  color: #444;
                  background: #EAEAEA;
              }

              %(crumbs_css)s
            </style>
          </head>
          <body>
            <div class="container-fluid radish-container">
                <div class="radish-sidebar">
                  <div class="radish-sidebar-header text-center">
                    Radish Documentation
                  </div>
                  %(toctree)s
                </div>
                <div class="radish-content">
                  <div class="text-right text-muted">
                    <small>
                      Generated by Radish-Docs
                      <strong>(beta)</strong>
                    </small>
                  </div>
                  %(crumbs)s
                  %(nav_links)s
                  %(content)s
                  <br />
                  %(nav_links_reverse)s
                </div>
            </div>
          </body>
        </html>
        """)

        # ~~~~~~~~~~~~~~~~~~~ #
        # generate content and strip any trailing newlines for it
        content = "".join(map(str, self._output_list))
        #content = content.rstrip("\n")

        # add content and title
        elements = {
            'title': self.title,
            'content': indent(content, width=10, skip_first_line=True),
            'toctree': toctree.output(depth_uri=self.depth_uri),
        }

        # ~~~~~~~~~~~~~~~~~~~ #
        # if crumbs are set and exist
        if crumbs is not None and len(crumbs) > 0:
            # add crumbs css
            # note: the dedent is here because of the triple quote
            #       the indent of 14 is here so the indentation matches
            #       the css block above
            elements['crumbs_css'] = indent(dedent("""\
                  .radish-breadcrumb {
                    margin-bottom: 0px;
                  }

                  /* use double right quote "»" character to separate
                     breadcrumbs instead of "/"; also make the breadcrumb
                     separator black for more visibility*/
                  .radish-breadcrumb > li + li:before {
                    color: #000;
                    content: "\\bb";
                  }"""),
                width=10, skip_first_line=True)

            # add crumbs html itself, indented by 6
            crumb_output = self._crumbs(crumbs)
            elements['crumbs'] = indent(crumb_output, width=6,
                                        skip_first_line=True)
            elements['nav_links'] = self._nav_links(previous_crumb,
                                                    next_crumb)
            elements['nav_links_reverse'] = self._nav_links(previous_crumb,
                                                            next_crumb,
                                                            reverse=True)
        else:
            # if no crumbs or empty crumbs do not include the css or
            # or any crumb html
            elements['crumbs_css'] = ''
            elements['crumbs'] = ''
            elements['nav_links'] = ''
            elements['nav_links_reverse'] = ''

        # ~~~~~~~~~~~~~~~~~~~ #
        # interpolate elements into
        output_ = html_source % elements
        # clean out any leadign whitespace
        output_ = strip_leading_whitespace(output_)

        return output_

    # ----------------------------------------------------------------------- #
    def add_line(self, text):
        if isinstance(text, string_types):
            self._output_list.append("%s\n" % text)
        else:
            self._output_list.append(text)

    # ----------------------------------------------------------------------- #
    def add_linebreak(self):
        self.add_line("<br />")

    # ----------------------------------------------------------------------- #
    def add_label(self, label):
        next_label = self._next_label(label)
        self.add_line('<a name="%s"></a>' % next_label)
        # "register" the label as used label
        self._labels[next_label] = None

    # ----------------------------------------------------------------------- #
    def add_comment(self, comment):
        self.add_line("<!-- %s -->" % comment)

    # ----------------------------------------------------------------------- #
    def add_heading(self, text, level):
        # ~~~~~~~~~~~~~ #
        tag = self._HEADINGS[level]

        # if the title is None (which means heading of level 0 has not been
        # specified yet)
        if self.title is None:
            # if heading is of level 0 then set the title to the heading text
            if level == 0:
                self.title = text
            else:
                # and level of the heading is not 0 raise error that that first
                # heading of the document must by of level 0
                msg ="first heading of the document should at level 0"
# TODO: raise RadishError
                raise ValueError(msg)
        else:
            # if title exists (is not None) and this heading is of level 0
            # raise and error saying that onely one heading of level 0 is
            # allowed
            if level == 0:
                msg ="only one heading of level 0 (document heading) allowed"
# TODO: raise RadishError
                raise ValueError(msg)

        # ~~~~~~~~~~~~~ #
        no_id_label = make_id(text)
        label = self._next_label(no_id_label)

        # ~~~~~~~~~~~~~ #
        link = ''
        link = '<%s id="%s">\n' % (tag, label)
        link += '  %s' % text
        link += '  <a class="headerlink fa fa-link" href="%s#%s" '\
                'title="Permalink to this headline">¶</a>' \
                          % (self.uri, label)
        link += '</%s>' % tag
        self.add_line(link)

        # ~~~~~~~~~~~~~ #
        # "register" the label with the document
        self._labels[label] = text
        # add the link to contents
        # if this is document heading (level is 0) then do not add an anchor
        if level == 0:
            self.contents.add_item(level, text, self.uri)
        else:
            self.contents.add_item(level, text, self.uri, anchor=label)

    # ----------------------------------------------------------------------- #
    def add_contents(self, depth, caption):
        self.contents.depth = depth
        self.contents.caption = caption
        self.contents.local = True
        self.add_line(self.contents)

    # ----------------------------------------------------------------------- #
    def add_toctree(self, maxdepth, caption):
        self._toctree.caption = caption
        self._toctree.maxdepth = maxdepth
        self._toctree.depth_uri = self.depth_uri
        self._toctree.documents = self._documents
        self.add_line(self._toctree)

    # ----------------------------------------------------------------------- #
    def add_ruler(self):
        self.add_line("<hr />")

    # ----------------------------------------------------------------------- #
    def add_table(self, data, headers=None, alignment=None):
        output = ""

        # if alignment is not passed in then create a default alignment to the
        # "left".  number of columns in the first data row is used to create
        # the tuple with alignment
        if alignment is None:
            alignment = ("left",) * len(data[0])

        all_rows = list(data)
        if headers is not None:
            all_rows.insert(0, headers)

        # calculate the column with in percentage value
        column_widths = calculate_column_widths(all_rows)
        widths_total = sum(column_widths)
        # round the percentage to 2 decimal points and multiply it by
        # 100 so it can be used with "%"
        # example: [73, 8, 6, 6, 6]
        column_width_percentage = [int(round(width/widths_total, 2) * 100)
                                      for width in column_widths]

        # start table
        output += "<table class='table table-bordered table-condensed table-striped'>\n"

        # add colgroup with percentage width
        output += "  <colgroup>\n"
        for column_width in column_width_percentage:
            output += "    <col width='%d%%'>\n" % column_width
            output += "    </col>\n"
        output += "  </colgroup>\n"


        if headers is not None:
            # add table heading if given
            output += "  <thead valign='bottom'>\n"
            output += "    <tr>\n"
            for column_index, text in enumerate(headers):
                align = alignment[column_index]
                output += "       <th align='%s'>%s</th>\n" % (align, text)
            output += "    </tr>\n"
            output += "  </thead>\n"

        # add table body
        output += "  <tbody valign='top'>\n"
        for row in data:
            output += "    <tr>\n"
            for column_index, text in enumerate(row):
                align = alignment[column_index]
                output += "       <td align='%s'>%s</td>\n" % (align, text)
            output += "    </tr>\n"
        output += "  </tbody>\n"

        # end table
        output += "</table>"

        # write the table to the document
        self.add_line(output)

    # ----------------------------------------------------------------------- #
    def add_field_list(self, table):
        # create "field" list as a table
        output = ""

        # start table
        output += "<table>\n"
        # add table body
        output += "  <tbody valign='top'>\n"
        for header, text in table:
            output += "    <tr>\n"
            output += "       <th align='right'>%s:</th>\n" % header
            output += "       <td>%s</td>\n" % text
            output += "    </tr>\n"
        output += "  </tbody>\n"
        # end table
        output += "</table>"

        # write the table to the document
        self.add_line(output)

    # ----------------------------------------------------------------------- #
    def add_index(self, entry):
        # there are no indices in html at this point
        pass

    # ----------------------------------------------------------------------- #
    def add_indices(self, indices):
        # there are no indices in html at this point
        pass

    # ----------------------------------------------------------------------- #
    def add_indented_paragraph(self, text):
        output = ""
        output += "<div class='panel panel-default'>\n"
        output += "  <div class='panel-body'>\n"
        output += "    %s\n" % text
        output += "  </div>\n"
        output += "</div>"
        self.add_line(output)

    # ----------------------------------------------------------------------- #
    def add_todo(self, text):
        output = ""
        output += "<div class='alert alert-danger'>\n"
        output += "  <strong>Todo!</strong>\n"
        output += "  %s\n" % text
        output += "</div>"
        self.add_line(output)

    # ----------------------------------------------------------------------- #
    def _next_label(self, no_id_label):
        # ~~~~~~~~~~~~~ #
        label_counts = set()
        for current_label in self._labels:
            # check if label has no -id prefix or if has a -id0 prefix
            # and add 0 to label count. We are checking for -id0 here since
            # the pattern below does not (or it wil be finding 0 prefixed
            # strings: 01, 02, 03)
            if    current_label == no_id_label \
               or current_label == "%s-id0" % no_id_label:

                if 0 in label_counts:
                    msg = "failed to make label due to duplicate id %d" % 0
                    raise Exception(msg)
                else:
                    label_counts.add(0)
                    continue
            else:
                # match a pattern of label with no id + suffix "-id" + number
                # to note, this does not match any pattern that has "-id"
                # suffix followed by 0 to avoid "0" prefixed "number" strings
                # the one exception to this, which is "id0" is addressed in
                # the if block above
                pattern = "^(%s)(-id)([1-9]+[0-9]*)$" % re.escape(no_id_label)
                matches = re.match(pattern, current_label)
                if matches is None:
                    continue
                else:
                    # ('hello', '-id', '2002')
                    _, _, count_text = matches.groups()
                    count = int(count_text)
                    if count in label_counts:
                        msg = "failed to make label due to duplicate id %d" \
                               % count
                        raise Exception(msg)
                    else:
                        label_counts.add(count)

        # could not find text of text+id, then this label is the first one
        if len(label_counts) == 0:
            label = no_id_label
        else:
            # get the top label id in the label count
            last_label_id = max(label_counts)
            # create full heading sequence set from 0 to last label id + 1
            full_label_sequence = set(range(0, last_label_id + 1))
            # get et difference between the full sequence and the label counts
            sequence_diff = full_label_sequence.difference(label_counts)
            # if there is no difference in sequence then then they are
            # identical and the next id is last label id + 1
            if len(sequence_diff) == 0:
                label_id = last_label_id + 1
                label = "%s-id%d" % (no_id_label, label_id)
            else:
                # othewise next id is the smallest number in the difference set
                label_id = min(sequence_diff)
                # if the label id is 0 the use no id label
                if label_id == 0:
                    label = no_id_label
                else:
                    # make the lavel with text ahd heading_id
                    label = "%s-id%d" % (text, label_id)

        return label
