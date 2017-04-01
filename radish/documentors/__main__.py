# -*- coding: utf-8 -*-

"""
This module provides a script to document Radish step implementations
"""

import os
import sys

from docopt import docopt

from radish import __VERSION__

from radish.documentors.html import MultiPageHtmlBook
from radish.documentors.html import SinglePageHtmlBook

from radish.documentors.sphinx import MultiPageSphinxBook
from radish.documentors.sphinx import SinglePageSphinxBook

from radish.documentors.writers.steps import StepsMultiPageWriter
from radish.documentors.writers.steps import StepsSinglePageWriter

from radish.errororacle import error_oracle, enable_excepthook
from radish.exceptions import RadishError
from radish.loader import load_module_assets
from radish.main import setup_config
from radish.stepregistry import StepRegistry


# ........................................................................... #
@error_oracle
def main():
    usage = """
Usage:
    radish-docs sphinx <steps-path>
        [-o=<folder-path> | --output-folder=<folder-path>]
        [--home-file-name=<file-path> ]
        [-s=<file-path> | --single-file=<file-path>]
        [-c | --print-to-console]
        [-l=<label-prefix> | --label-prefix=<label-prefix>]
        [-w | --overwrite]
        [--no-ansi]
    radish-docs html <steps-path>
        [-o=<folder-path> | --output-folder=<folder-path>]
        [--home-file-name=<file-path> ]
        [-s=<file-path> | --single-file=<file-path>]
        [-c | --print-to-console]
        [-w | --overwrite]
        [--no-ansi]
    radish-docs (-h | --help)
    radish-docs (-v | --version)

Commands:
    sphinx                                            create Sphinx documentation
    html                                              create HTML documentation

Arguments:
    steps-path                                        path to python step modules to document

Options:
    -o=<folder-path>, --output-folder=<folder-path>   location of the output folder,
                                                      by default `_build` in the current working folder
    --home-file-name=<file-name>                      optional, name for the home file created by `--output-folder`,
                                                      by default "index.rst"; this file is placed in the output folder
    -s=<file-path>, --single-file=<file-path>         write documentation to a single file
    -c, --print-to-console                            print `--single-file` documentaiton to console
    -l=<label-prefix>, --label-prefix=<label-prefix>  label prefix used for various section of the generated docs,
                                                      used if you need a unique ids on in your documentation.
                                                      Default is `radish_docs.`
    -w, --overwrite                                   overwrite output folder or file by removing and creating it again
    -h, --help                                        show this screen
    -v, --version                                     show version

(C) Copyright by Timo Furrer <tuxtimo@gmail.com>
"""

    # default to "internal software error" error code as per sysexits.h
    return_code = 70

    # enable errororacles except hook system wide
    enable_excepthook()

    # parse sys.argv against our docopt argments
    arguments = docopt("radish-docs {0}\n{1}".format(__VERSION__, usage),
                       version=__VERSION__)

    # create world wide configuration
    setup_config(arguments)

    # html command
    if arguments['html']:
        # get the module path
        steps_path = arguments['<steps-path>']

        # get the output folder or if missing set the default for the
        # output_folder_path
        if arguments['--output-folder'] is not None:
            output_folder_path = arguments['--output-folder']
        else:
            # create default by joing current folder and '_build'
            output_folder_path = os.path.join(os.getcwd(), '_build')

        # get the home file name, otherwise default it to index.rst
        if arguments['--home-file-name'] is not None:
            home_file_name = arguments['--home-file-name']
            # test if given file name rather then path, raises RadishError
            _test_file_name(home_file_name, '--home-file-name')
        else:
            home_file_name = "index.html"

        # set single file path argument
        single_file_path = arguments['--single-file']

        # set overwrite flag
        overwrite = arguments['--overwrite']

        # set print to console flag
        print_to_console = arguments['--print-to-console']
        # if console is specified then then set single file to none and
        # output_folder_path to None, overwrite to False
        if print_to_console:
            single_file_path = None
            output_folder_path = None
            overwrite = False

        # run html documentation
        return_code = document_with_html(steps_path,
                                         output_folder_path,
                                         home_file_name,
                                         single_file_path,
                                         overwrite)
    # sphinx command
    elif arguments['sphinx']:
        # get the module path
        steps_path = arguments['<steps-path>']

        # get the output folder or if missing set the default for the
        # output_folder_path
        if arguments['--output-folder'] is not None:
            output_folder_path = arguments['--output-folder']
        else:
            # create default by joing current folder and '_build'
            output_folder_path = os.path.join(os.getcwd(), '_build')

        # get the home file name, otherwise default it to index.rst
        if arguments['--home-file-name'] is not None:
            home_file_name = arguments['--home-file-name']
            # test if given file name rather then path, raises RadishError
            _test_file_name(home_file_name, '--home-file-name')
        else:
            home_file_name = "index.rst"

        # set single file path argument
        single_file_path = arguments['--single-file']

        # set label prefix
        if arguments['--label-prefix'] is not None:
            label_prefix = arguments['--label-prefix']
        else:
            label_prefix = "radish_docs."

        # set overwrite flag
        overwrite = arguments['--overwrite']

        # set print to console flag
        print_to_console = arguments['--print-to-console']
        # if console is specified then then set single file to none and
        # output_folder_path to None, overwrite to False
        if print_to_console:
            single_file_path = None
            output_folder_path = None
            overwrite = False

        # run sphinx documentation
        return_code = document_with_sphinx(steps_path,
                                           output_folder_path,
                                           home_file_name,
                                           single_file_path,
                                           overwrite,
                                           print_to_console,
                                           label_prefix)
    else:
        # as far as I can tell, this is never reached since the commands
        # are mandatory. It is also unnecessary to print docopt usage since
        # docopt does it itself
        pass

    return return_code



# ........................................................................... #
def document_with_html(steps_path, output_folder_path=None,
                       home_file_name="index.html", single_file_path=None,
                       overwrite=False, print_to_console=False,):

    # important: "normalizing" the path before imports resolve 99% of the
    # issues related to having ".", ".." and "/" in the
    clean_steps_path = os.path.normpath(steps_path)

    # if clean steps path is a folder then it is the basedir otherwise basedir
    # is the parent folder name of the clean steps path
    if os.path.isdir(clean_steps_path) is True:
        clean_basedir = clean_steps_path
    else:
        clean_basedir = os.path.dirname(clean_steps_path)

    # load all the step paths assets
    load_module_assets(clean_steps_path)

    # get the steps which will be documented
    steps = StepRegistry().steps

    # create steps writer
    steps_writer = StepsSinglePageWriter(steps, basedir=clean_basedir)

    if print_to_console is True:
        # for console we default the home file path to radish.rst since
        # it really does not matter what it is
        book = SinglePageHtmlBook(file_path="radish.html")
        # write steps documentation to the book
        steps_writer.write_to(book)
        # print bookl to console
        book.print_to_console()

    elif single_file_path is not None:
        # create single page html document, which is actually set of document
        # sections

        # get the filename only
        single_file_name = os.path.split(single_file_path)[1]
        book = SinglePageHtmlBook(file_path=single_file_name)

        # write steps documentation to the book
        steps_writer.write_to(book)
        # write generated documentation to a file
        book.write_file(single_file_path, overwrite)

    else:
        # create multipage steps writer
        steps_writer = StepsMultiPageWriter(steps, basedir=clean_basedir)
        # home_file_name is our home_file_path since all the paths are
        # relative to the output_folder
        book = MultiPageHtmlBook(home_file_path=home_file_name)

        # write steps documentation to the book
        steps_writer.write_to(book)

        # write generated documentation to a files
        book.write_files(output_folder_path, overwrite)


# ........................................................................... #
def document_with_sphinx(steps_path, output_folder_path=None,
                         home_file_name="index.rst", single_file_path=None,
                         overwrite=False, print_to_console=False,
                         label_prefix="radish_docs."):

    # important: "normalizing" the path before imports resolve 99% of the
    # issues related to having ".", ".." and "/" in the
    clean_steps_path = os.path.normpath(steps_path)

    # if clean steps path is a folder then it is the basedir otherwise basedir
    # is the parent folder name of the clean steps path
    if os.path.isdir(clean_steps_path) is True:
        clean_basedir = clean_steps_path
    else:
        clean_basedir = os.path.dirname(clean_steps_path)

    # load all the step paths assets
    load_module_assets(clean_steps_path)

    # get the steps which will be documented
    steps = StepRegistry().steps

    # if there is no output folder and single file is specified then
    # output to console
    if print_to_console is True:

        # create single page steps writer
        steps_writer = StepsSinglePageWriter(steps, basedir=clean_basedir)

        # for console we default the home file path to radish.rst since
        # it really does not matter what it is
        # create single page sphinx book
        book = SinglePageSphinxBook(file_path="radish.rst",
                                    label_prefix=label_prefix)

        # write steps documentation to the book
        steps_writer.write_to(book)

        # print book to console
        book.print_to_console()

    elif single_file_path is not None:

        # create single page steps writer
        steps_writer = StepsSinglePageWriter(steps, basedir=clean_basedir)
        # get the filename only
        single_file_name = os.path.split(single_file_path)[1]
        # create single page sphinx book
        book = SinglePageSphinxBook(file_path=single_file_name,
                                    label_prefix=label_prefix,)
        # write steps documentation to the book
        steps_writer.write_to(book)
        # write generated documentation to a file
        book.write_file(single_file_path, overwrite)
    else:

        # create multipage steps writer
        steps_writer = StepsMultiPageWriter(steps, basedir=clean_basedir)
        # home_file_name is our home_file_path since all the paths are
        # relative to the output_folder
        book = MultiPageSphinxBook(home_file_path=home_file_name,
                                   label_prefix=label_prefix,)

        # write steps documentation to the book
        steps_writer.write_to(book)

        # write generated documentation to a files
        book.write_files(output_folder_path, overwrite)

    # for now always return 0, error oracle will take care of other error codes
    return 0


# ........................................................................... #
def _test_file_name(file_name, command_line_option):
    if os.path.split(file_name) != ('', file_name):
        msg = "%s value should be a file name not a file path: %s" % \
            (command_line_option, command_line_option)
        raise RadishError(msg)


# ........................................................................... #
if __name__ == "__main__":
    sys.exit(main())
