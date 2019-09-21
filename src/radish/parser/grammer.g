start: _NEWLINE* feature?

// A Tag which can be used on a Feature
feature_tag: std_tag | constant_tag

// A Tag which can be used on a Scenario
scenario_tag: std_tag | precondition_tag | constant_tag

// A standard gherkin Tag in the form of:
// * @tag
std_tag: "@" STRING_NO_WS _NEWLINE?

// A radish Precondition Tag in the form of:
// * @precondition(feature: scenario)
precondition_tag: "@precondition(" STRING_NO_COLON_NL ":" STRING_NO_PAREN_NL ")" _NEWLINE?

// A radish Constant Tag in the form of:
// * @constant(name: value)
constant_tag: "@constant(" STRING_NO_COLON_NL ":" STRING_NO_PAREN_NL ")" _NEWLINE?

// A Feature may contain:
//   * An optional description consisting of multiple free textline, but without
//     a keyword appearing at the start.
//   * An optional `Background` block containing any number of `step`s.
//   * Any number of `Scenario` blocks continaing any number of `step`s.
//feature: tag* FEATURE TEXTLINE feature_inner?
feature: feature_tag* FEATURE ":" STRING_NO_NL _NEWLINE feature_body?
feature_body: description background? (rule | scenario | scenario_outline | scenario_loop | _NEWLINE)*

// A description consists of any textlines, but the description ends if one of
// the following keyword appears at the start of the line:
// * `Feature:`
// * `Background:`
// * `Example:`
// * `Scenario:`
// * `Scenario Outline:`
// * `Rule:`
description: (STRING_NO_NL | _NEWLINE)+

// A Rule represents a Business Rule. It can contain Scenarios
rule: RULE ":" STRING_NO_NL _NEWLINE (scenario | scenario_outline | scenario_loop | _NEWLINE)*

// A Background block consists of a sentence following the `Background` keyword
// and any number of steps
background: BACKGROUND ":" STRING_NO_NL? _NEWLINE (step | _NEWLINE)*

// A Scenario block consists of a sentence following the `Scenario` keyword
// and any number of steps
scenario: scenario_tag* (SCENARIO | EXAMPLE) ":" STRING_NO_NL _NEWLINE (step | _NEWLINE)*

// A Scenario Outline block consists of a sentence following the `Scenario Outline` keyword,
// any number of steps and an Examples block followed by a table with parameters for the
// outlined steps.
scenario_outline: scenario_tag* (SCENARIO_OUTLINE | EXAMPLE_OUTLINE) ":" STRING_NO_NL _NEWLINE (step | _NEWLINE)* examples

// An Examples block is used to parametrize a 'Scenario Outline'
// It's a table of data
examples: _EXAMPLES ":" _NEWLINE example_row example_row+

example_row: "|" (example_cell "|")+ _NEWLINE
example_cell: STRING_NO_VBAR

// A Scenario Loop block consists of a sentence following the `Scenario Loop` keyword,
// any number of steps and an `Iterations` block followed by a max iteration number.
scenario_loop: scenario_tag* (SCENARIO_LOOP | EXAMPLE_LOOP) ":" STRING_NO_NL _NEWLINE (step | _NEWLINE)* iterations

// An Iterations block indicates the max number of iterations for a `Scenario Loop`.
iterations: _ITERATIONS ":" INT

// A step is a textline beginning with `Given`, `When`, `Then`, `And` and `But`.
step: (GIVEN | WHEN | THEN | AND | BUT) STRING_NO_NL _NEWLINE step_arguments
step_arguments: step_doc_string? _NEWLINE? step_data_table?

// A step data table is additional tabular data for the previous step
step_data_table: step_data_table_row+
step_data_table_row: "|" (step_data_table_cell "|")+ _NEWLINE
step_data_table_cell: STRING_NO_VBAR

// A step doc string is additional multilined text data for the previous step
step_doc_string: DOC_STRING_DELIMITER _NEWLINE (STRING_NO_NL? _NEWLINE)* DOC_STRING_DELIMITER

// Keywords
FEATURE: "Feature"i
BACKGROUND: "Background"i
RULE: "Rule"i
EXAMPLE: "Example"i
SCENARIO: "Scenario"i
SCENARIO_OUTLINE: "Scenario Outline"i
EXAMPLE_OUTLINE: "Example Outline"i
_EXAMPLES: "Examples"i
SCENARIO_LOOP: "Scenario Loop"i
EXAMPLE_LOOP: "Example Loop"i
_ITERATIONS: "Iterations"i
GIVEN: "Given"i
WHEN: "When"i
THEN: "Then"i
AND: "And"i
BUT: "But"i

// terminals used to match things
TEXTLINE.0: /.*\n/
STRING_NO_COLON_NL.0: /[^\n:]/+
STRING_NO_PAREN_NL.0: /[^\n\)\(]/+
STRING_NO_NL.0: /[^\n]/+
_NEWLINE: /\n/
STRING_NO_WS.0: /[^ \t\f\r\n]/+
STRING_NO_VBAR.0: /((?<!\\)\\\||[^\|\f\r\n])+/
DOC_STRING_DELIMITER: "\"\"\""
COMMENT: /#[^\n]*\n/

%import common (WS_INLINE)
%import common (INT)
%ignore WS_INLINE
%ignore COMMENT
