# -*- coding: utf-8 -*-

import inspect

from collections import OrderedDict

from radish.utils import expandpath


# ........................................................................... #
class StepDefintionModule(object):

    _TITLE = "Module Overview"

    # ----------------------------------------------------------------------- #
    def __init__(self, file_path, basedir):
        # module file path
        self._file_path = file_path
        # module base folder
        self._basedir = basedir
        # module name for this module,
        self._module_name = inspect.getmodulename(self._file_path)
        # step defintions that will be added to this module
        self._step_definitions = []
        # output "collector" for this class
        self._output = ""

        self.relative_file_path = self._make_basedir_relative_file_path()
        # initialize the types dictionary used for to sort step additions
        self._step_definitions_by_type = \
            dict((step_type, []) for step_type in StepDefinition.SORTED_TYPES)

    # ----------------------------------------------------------------------- #
    def add(self, step_definition):
        # append the step definition by type dictionary
        step_type = step_definition.type
        self._step_definitions_by_type[step_type].append(step_definition)

        # create a sorted list of the step defintions
        # the sort is by type as specified in StepDefinition.ALL_TYPES
        step_definitions = []
        for step_type in StepDefinition.SORTED_TYPES:
            step_definitions.extend(self._step_definitions_by_type[step_type])

        # set self._step_definitions to a copy of step_definitions
        self._step_definitions = step_definitions[:]

    # ----------------------------------------------------------------------- #
    def write_to(self, document, heading_level, with_contents):
        # ~~~~~~~~~~~~~~~~ #
        # add a commment with file_path in it
        document.add_comment(self.relative_file_path)

        # ~~~~~~~~~~~~~~~~ #
        # add document label
        label = document.make_label_from_file_path(self.relative_file_path,
                                                   document.label_prefix)
        document.add_label(label)

        # ~~~~~~~~~~~~~~~~ #
        # add index with the module entry
        document.add_index(self._module_name)

        # ~~~~~~~~~~~~~~~~ #
        # add module_name as the document heading
        document.add_heading(self.relative_file_path, heading_level + 0)

        # if with_contents is set then add table of contents
        if with_contents is True:
            document.add_contents(depth=2, caption="Contents")

        # ~~~~~~~~~~~~~~~~ #
        # add heading for this section
        document.add_heading(self._TITLE, heading_level + 1)

        # ~~~~~~~~~~~~~~~~ #
        # add field list item for module
        # add field list item for file name
        module_information = (
            ("Module", self._module_name),
            ("File name", self.relative_file_path)
        )
        document.add_field_list(module_information)

        # ~~~~~~~~~~~~~~~~ #
        # generate step defintions overview section
        step_definitions_overview = \
            StepDefinitionsOverview(self._step_definitions)
        # add step definitions overview section
        step_definitions_overview.write_to(document, heading_level)

        # ~~~~~~~~~~~~~~~~ #
        # generate step definitions section
        step_definitions = StepDefinitions(self._step_definitions)
        step_definitions.write_to(document, heading_level)

    # ----------------------------------------------------------------------- #
    def _make_basedir_relative_file_path(self):

        # expand and normalize the file path
        clean_file_path = expandpath(self._file_path)
        clean_basedir = expandpath(self._basedir) + "/"

        # if the file_path is within the basedir then remove basedir from th
        # clean_file path
        if clean_file_path.startswith(clean_basedir):
            # remove the basedir prefix + '/' from the file path
            basedir_relative_file_path = clean_file_path[len(self._basedir)+1:]
        else:
            basedir_relative_file_path = clean_file_path

        return basedir_relative_file_path


# ........................................................................... #
class StepDefinitionsOverview(object):

    _TITLE = "Steps Overview"
    _HEADERS = ('Step Definition', 'Given', 'When', 'Then', 'Step')
    _STEP_MAP = {
        'Given': ("x", " ", " ", " "),
        'When': (" ", "x", " ", " "),
        'Then': (" ", " ", "x", " "),
        'Step': ("x", "x", "x", "x"),
    }

    _TABLE_ALIGNMENT = ["left", "center", "center", "center", "center"]

    # ----------------------------------------------------------------------- #
    def __init__(self, step_definitions):

        # step definition collection
        self._step_definitions = step_definitions
        # output "collector" for this class
        self._output = ""

    # ----------------------------------------------------------------------- #
    def write_to(self, document, heading_level):

        # add heading for this section using "=" underline character
        document.add_heading(self._TITLE, heading_level + 1)

        data_rows = []
        # go over each step and append it to the data_rows
        for step_definition in self._step_definitions:
            # make a typle out of the full sentence and the "x" marks for
            # each step
            row = (step_definition.full_sentence,) \
                   + self._STEP_MAP[step_definition.type]
            data_rows.append(row)
        # add table
        document.add_table(data_rows, self._HEADERS, self._TABLE_ALIGNMENT)


# ........................................................................... #
class StepDefinitions(object):

    _TITLE = "Step Definitions"

    # ----------------------------------------------------------------------- #
    def __init__(self, step_definitions):
        # step defintions
        self._step_definitions = step_definitions
        # output "collector" for this class
        self._output = ""

    # ----------------------------------------------------------------------- #
    def add(self, step_definition):
        # append the step to out collections
        self._step_definitions.append(step_definition)

    # ----------------------------------------------------------------------- #
    def write_to(self, document, heading_level):

        # add heading for this section using "=" underline character
        document.add_heading(self._TITLE, heading_level + 1)

        # go over each step definition adding
        #  - step definition ..index role
        #  - step definition header underlined by "-"
        #  - either a step defintion docstring or a "..todo" mention that step
        #    definition documenation is missing
        for step_definition in self._step_definitions:
            # add step definition index
            self._write_step_definition_indices(step_definition, document)
            # create step definition header out full_sentence
            step_header = step_definition.full_sentence
            # add add step header with "-" underline character
            document.add_heading(step_header, heading_level + 2)
            # callable
            step_code_information = '%s "%s" on line %d' \
                % (step_definition.callable_type.capitalize(),
                   step_definition.callable_name,
                   step_definition.callable_line_no)

            step_information = [
                ("Source", step_code_information),
            ]

            # write table with source
            document.add_table(step_information)

            # add step defintion docstring or a todo if docstring is missing
            if step_definition.doc_string is None:
                document.add_todo("Step definition documentation is missing.")
            else:
                document.add_indented_paragraph(step_definition.doc_string)

    # ----------------------------------------------------------------------- #
    def _write_step_definition_indices(self, step_definition, document):

        step_defintion_indices = []

        # go over each possible alias for the step defintions
        typed_sentences = step_definition.typed_sentences.items()
        for step_definition_type, full_sentence in typed_sentences:
            # if the step_type is not named (a.k.a 'Step') then
            # index line is set to "Step;" + full_sentence
            # otherwise index will be "<name of step>" + step + full_sentence
            if step_definition_type == 'Step':
                entry = "Step"
                subentry = full_sentence
            else:
                entry = "%s step" % step_definition_type
                subentry = full_sentence

            step_defintion_indices.append((entry, subentry))

        # add the indicies
        document.add_indices(step_defintion_indices)


# ........................................................................... #
class StepDefinition(object):

    # create "enum" of explicit step definition types
    EXPLICIT_TYPES = ['Given', 'When', 'Then']
    # create "enum" of all step definition types
    ALL_TYPES = EXPLICIT_TYPES + ['Step']
    # create sorted "enum" of  of all step definition types
    SORTED_TYPES = ALL_TYPES

    # ----------------------------------------------------------------------- #
    def __init__(self, pattern, callable_):
        # step pattern string
        self._pattern = pattern
        # step callable (function or class)
        self._callable = callable_
        # callable name
        self.callable_name = callable_.__name__
        # callable type
        self.callable_type = callable_.__class__.__name__
        # line number of the callable including any decorators
        self.callable_line_no = inspect.getsourcelines(callable_)[1]
        # docstring of the step callable
        self.doc_string = inspect.getdoc(callable_)
        # type of the step
        self.type = self._determine_type()
        # list all possible step aliases. For named steps such as given, then
        # when the list contains just that name. For unnamed step it set to
        # list of all possible statps
        self.aliases = self._determine_alias()
        # step's full sentence, including the verb (given, when then)
        # for unnamed stop the step verb is Given/Then/When
        self.full_sentence = self._compile_full_sentence()
        # list of all possible steps senteces. For named steps the list
        # contains only the full sentence. For unamed step the list is made up
        # of list of possible named steps (given, when, then) + sentence
        self.typed_sentences = self._compile_typed_sentences()

    # ----------------------------------------------------------------------- #
    def __repr__(self):
        return "<%s (%s): %s; %s>" % (self.__class__.__name__, hex(id(self)),
                                      self.type, self.full_sentence)

    # ----------------------------------------------------------------------- #
    def _determine_type(self):
        word = self._pattern.split(' ')[0].capitalize()
        if word in self.EXPLICIT_TYPES:
            step_type = word
        else:
            step_type = "Step"

        return step_type

    # ----------------------------------------------------------------------- #
    def _determine_alias(self):
        if self.type == "Step":
            aliases = ['Given', 'When', 'Then', 'Step']
        else:
            aliases = [self.type]

        return aliases

    # ----------------------------------------------------------------------- #
    def _compile_typed_sentences(self):
        # if type is Step, create sentences for each of the type prefixed with
        # the type. As exception for the 'Step' type use full sentence
        # in short:
        #  [Given] = "Given " + pattern
        #  [When]  = "When "  + pattern
        #  [Then]  = "Then "  + pattern
        #  [Step]  = "Given/When/Then" + pattern
        sentences = OrderedDict()
        if self.type == 'Step':
            for alias in self.aliases:
                if alias == 'Step':
                    sentences[alias] = self.full_sentence
                else:
                    sentences[alias] = "%s %s" % (alias, self._pattern)
        else:
            sentences[self.type] = self.full_sentence

        return sentences

    # ----------------------------------------------------------------------- #
    def _compile_full_sentence(self):
        # if type is Step, the full sentence is "Given/When/Then" + pattern
        if self.type == 'Step':
            sentence = "Given/When/Then %s" % self._pattern
        # for all other steps the sentect is the pattern
        else:
            sentence = self._pattern

        return sentence
