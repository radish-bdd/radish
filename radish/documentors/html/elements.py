# -*- coding: utf-8 -*-

import sys

from radish.documentors.utils import indent

from .utils import safe_url_join

# ........................................................................... #
class TocTree(object):

    # ----------------------------------------------------------------------- #
    def __init__(self):
        # this class mostly mirrors the behavior of the RST toctree role

# TODO: do we needs a default caption?
        self.caption = None
        # default maxdepth to largest python supported int.
        self.maxdepth = sys.maxsize
        self.documents = None
        self.depth_uri = None

    # ----------------------------------------------------------------------- #
    def set_documents(self, documents):
        self.documents = documents

    # ----------------------------------------------------------------------- #
    def output(self, documents=None, depth=None, with_caption=True,
               depth_uri=None):

        # if documents are not given, set them to the documents of the instance
        if documents is None:
            documents = self.documents

        # if depth is not given then set it to the maxdepth of the instance
        if depth is None:
            depth = self.maxdepth

        # if depth_uri is not given then set it to the depth_uri of the
        # instance
        if depth_uri is None:
            depth_uri = self.depth_uri


        output_ = ""

        # add caption if with_caption is true
        if with_caption is True and self.caption is not None:
            output_ += "<p>\n"
            output_ += "  <strong>%s:</strong>\n" % self.caption
            output_ += "</p>\n"

        # get the html list created from recursing into the contents of all
        # the documents
        html_list = self._recurse_documents_contents(documents)
        # add output of the html list with passed in depth and relative to the
        # passed in path
        output_ += html_list.output(depth, depth_uri)

        return output_

    # ----------------------------------------------------------------------- #
    def __str__(self):
        # render output using defaults
        return self.output()

    # ----------------------------------------------------------------------- #
    def _recurse_documents_contents(self, documents):

        # create new html list to contain all the <li> entries from each
        # documents content
        html_list = HtmlList()
        for document in documents:
            # update the html list with <li> entries from the document contents
            # html list
            html_list.items.extend(document.contents.html_list_items())
            # and subentries from the child documents of this document
            if len(document._documents) > 0:
                # create the <li> item which will be the parent to the html
                # list for the child documents <li> items
                wrapper_item = HtmlListItem()
                # set the list of of the wrapper <li> to the the html list
                # of the child documents as returned by this function
                wrapper_item.list = \
                    self._recurse_documents_contents(document._documents)
                # append the wrapper item to the html list <li> items
                html_list.items.append(wrapper_item)

        return html_list

# ........................................................................... #
class Contents(object):

    # ----------------------------------------------------------------------- #
    def __init__(self):
        # this mostly mirrors the behavior of the RST content tag
# TODO: I think there needs to be a default caption
        self.caption = None
        # default depth to largest python supported int.
        self.maxdepth = sys.maxsize
        self.local = False
        self._list = None

    # ----------------------------------------------------------------------- #
    def add_item(self, level, text, uri, anchor=None):

        # ~~~~~~~~~~~ #
        link = HtmlA(text, uri, anchor)
        item = HtmlListItem(body=link)

        # ~~~~~~~~~~~ #
        if self._list is None:
            if level == 0:
                # create html list
                self._list = HtmlList()
            else:
                msg = "first heading for the html list must be at level 0"
# TODO: RadishError
                raise Exception(msg)

        # add item
        self._list.add_to_list(item, level)

    # ----------------------------------------------------------------------- #
    def html_list_items(self):
        return self._list.items

    # ----------------------------------------------------------------------- #
    def output(self, depth, with_caption=True, skip_first=False,
               depth_uri=None):

# TODO: with toctree rewrite we no longer need output method, right?

        output = ""
        # add caption if not none
        if with_caption is True:
            if self.caption is not None:
                output += "<p>\n"
                output += "  <strong>%s:</strong>\n" % self.caption
                output += "</p>\n"

        # if only return local content then get the list of the first item
        # notable since there should be only 1 document heading heading that
        # list always has only 1 item
        if skip_first is True:
            output += self._list.items[0].list.output(depth, depth_uri)
        else:
            # otherwise return the whole list
            output += self._list.output(depth, depth_uri)

        return output

    # ----------------------------------------------------------------------- #
    def __str__(self):
        with_caption = self.caption is not None
        skip_first = self.local
        return self.output(self.depth, with_caption, skip_first,
                           depth_uri=None)


# ........................................................................... #
class HtmlList(object):

    # ----------------------------------------------------------------------- #
    def __init__(self):
        self.items = []

    # ----------------------------------------------------------------------- #
    def __len__(self):
        return len(self.items)

    # ----------------------------------------------------------------------- #
    def add_to_list(self, item, level):
        if level == 0:
            self.items.append(item)
        else:
            if len(self.items) == 0:
                msg = "can not add item at level more then 1 deeper then list "
                msg += "list depth. basically, you are trying to add a list "
                msg += "item to a non existent parent"
# TODO: raise a RadishError
                raise Exception(msg)
            else:
                last_item_list = self.items[-1].list
                last_item_list.add_to_list(item, level - 1)

    # ----------------------------------------------------------------------- #
    def output(self, depth, depth_uri):
        output_ = ""

        # if depth passed in is 0 do not output the list  since we reached the
        # depth set on this contents object
        if depth == 0:
            output_ = ""
        else:
            if len(self.items) > 0:
                output_ += "<ul>\n"
                for item in self.items:
                    # indent by 2 space since we are inside ul
                    item_output = item.output(depth, depth_uri)
                    output_ += indent(item_output, 2)
                output_ += "</ul>\n"

        return output_


# ........................................................................... #
class HtmlListItem(object):

    # ----------------------------------------------------------------------- #
    def __init__(self, body=None):
        self.body = body
        self.list = HtmlList()

    # ----------------------------------------------------------------------- #
    def output(self, depth, depth_uri):
        output_ = ""

        # ~~~~~~~~~~~~~~~~ #
        # open li tag
        output_ += "<li>\n"

        # ~~~~~~~~~~~~~~~~ #
        # add body if is not None, indenting it by 2
        if self.body is not None:
            # if item has output property, we assume it is a method
            # and call it to get output
            if hasattr(self.body, 'output') is True:
                body_output = self.body.output(depth_uri)
            else:
                # otherwise just get the str of the body
                body_output = str(self.body)

            # add the body output
            output_ += indent("%s\n" % body_output, 2)

        # ~~~~~~~~~~~~~~~~ #
        # add list if has length greater the 0, indenting it by 2
        # the passed in depth is subtracted by 1 since this is the child
        # list
        if len(self.list) > 0:
            list_output = self.list.output(depth - 1, depth_uri)
            output_ += indent(list_output, width=2)

        # ~~~~~~~~~~~~~~~~ #
        # close li tag
        output_ += "</li>\n"

        return output_


# ........................................................................... #
class HtmlA(object):

    # ----------------------------------------------------------------------- #
    def __init__(self, text, uri, anchor=None):
        self.text = text
        self.uri = uri
        self.anchor = anchor

    # ----------------------------------------------------------------------- #
    def output(self, depth_uri):
        # depth_uri is None then the content is for the local document
        if depth_uri is None:
            output_ = '<a href="#%s">%s</a>' % (self.anchor, self.text)
        else:
            uri = safe_url_join(depth_uri, self.uri)
            if self.anchor is None:
                output_ = '<a href="%s">%s</a>' % (uri, self.text)
            else:
                output_ = '<a href="%s#%s">%s</a>' \
                            % (uri, self.anchor, self.text)


        return output_
