"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import json
import re
from pathlib import Path

from lark import Lark, UnexpectedInput

from radish.models import PreconditionTag
from radish.parser.errors import (
    RadishLanguageNotFound,
    RadishMisplacedBackground,
    RadishMissingFeatureShortDescription,
    RadishMissingRuleShortDescription,
    RadishMissingScenarioShortDescription,
    RadishMultipleBackgrounds,
    RadishPreconditionScenarioDoesNotExist,
    RadishPreconditionScenarioRecursion,
    RadishScenarioLoopInvalidIterationsValue,
    RadishScenarioLoopMissingIterations,
    RadishScenarioOutlineExamplesInconsistentCellCount,
    RadishScenarioOutlineExamplesMissingClosingVBar,
    RadishScenarioOutlineExamplesMissingOpeningVBar,
    RadishScenarioOutlineWithoutExamples,
    RadishStepDataTableMissingClosingVBar,
    RadishStepDocStringNotClosed,
    RadishStepDoesNotStartWithKeyword,
)
from radish.parser.transformer import RadishGherkinTransformer, Transformer


class LanguageSpec:
    """Represents a gherkin language specification"""

    def __init__(self, code, keywords):
        self.code = code
        self.keywords = keywords
        self.first_level_step_keywords = {
            keywords["Given"],
            keywords["When"],
            keywords["Then"],
        }

    def __str__(self):
        return self.code

    def __call__(self, terminal):
        try:
            terminal.pattern.value = self.keywords[terminal.pattern.value]
        except KeyError:
            pass


class FeatureFileParser:
    """Radish Feature File Parser responsible to parse a single Feature File"""

    def __init__(
        self,
        grammerfile: Path = None,
        ast_transformer: Transformer = RadishGherkinTransformer,
        resolve_preconditions: bool = True,
    ) -> None:
        if grammerfile is None:
            grammerfile = Path(__file__).parent / "grammer.g"

        self.grammerfile = grammerfile
        self.resolve_preconditions = resolve_preconditions

        if ast_transformer is not None:
            self._transformer = ast_transformer()
        else:
            self._transformer = None

        self._current_feature_id = 1

        self._parsers = {}

    def _get_parser(self, language_spec):
        """Get a parser and lazy create it if necessary"""
        try:
            return self._parsers[language_spec.code]
        except KeyError:
            parser = Lark.open(
                str(self.grammerfile),
                parser="lalr",
                transformer=self._transformer,
                edit_terminals=language_spec,
            )
            self._parsers[language_spec.code] = parser
            return parser

    def parse(self, featurefile: Path):
        """Parse the given Feature File"""
        ast = self.parse_file(featurefile, self._current_feature_id)
        self._current_feature_id += 1
        if self.resolve_preconditions:
            self._resolve_preconditions(featurefile.parent, ast, {ast.path: ast})
        return ast

    def parse_file(self, featurefile: Path, feature_id: int = 0):
        """Parse the given Feature File using the parser"""
        with open(str(featurefile), "r", encoding="utf-8") as featurefile_f:
            contents = featurefile_f.read()
            return self.parse_contents(featurefile, contents, feature_id)

    def parse_contents(
        self, featurefile_path: Path, featurefile_contents: str, feature_id: int = 0
    ):
        # evaluate the language for the Feature File content
        language_spec = self._detect_language(featurefile_contents)

        # prepare the transformer for the Feature File
        if self._transformer is not None:
            self._transformer.prepare(
                language_spec, featurefile_path, featurefile_contents, feature_id
            )

        # get a parser
        parser = self._get_parser(language_spec)

        try:
            ast = parser.parse(featurefile_contents)
        except UnexpectedInput as exc:
            exc_class = exc.match_examples(
                parser.parse,
                {
                    RadishMissingFeatureShortDescription: RadishMissingFeatureShortDescription.examples,  # noqa
                    RadishMissingRuleShortDescription: RadishMissingRuleShortDescription.examples,
                    RadishMissingScenarioShortDescription: RadishMissingScenarioShortDescription.examples,  # noqa
                    RadishMisplacedBackground: RadishMisplacedBackground.examples,
                    RadishStepDoesNotStartWithKeyword: RadishStepDoesNotStartWithKeyword.examples,
                    RadishStepDocStringNotClosed: RadishStepDocStringNotClosed.examples,
                    RadishScenarioOutlineWithoutExamples: RadishScenarioOutlineWithoutExamples.examples,  # noqa
                    RadishScenarioOutlineExamplesMissingOpeningVBar: RadishScenarioOutlineExamplesMissingOpeningVBar.examples,  # noqa
                    RadishMultipleBackgrounds: RadishMultipleBackgrounds.examples,
                    RadishStepDataTableMissingClosingVBar: RadishStepDataTableMissingClosingVBar.examples,  # noqa
                    RadishScenarioLoopMissingIterations: RadishScenarioLoopMissingIterations.examples,  # noqa
                    RadishScenarioLoopInvalidIterationsValue: RadishScenarioLoopInvalidIterationsValue.examples,  # noqa
                    RadishScenarioOutlineExamplesMissingClosingVBar: RadishScenarioOutlineExamplesMissingClosingVBar.examples,  # noqa
                    RadishScenarioOutlineExamplesInconsistentCellCount: RadishScenarioOutlineExamplesInconsistentCellCount.examples,  # noqa
                },
            )
            if not exc_class:
                raise
            raise exc_class(exc.get_context(featurefile_contents), exc.line, exc.column)
        return ast

    def _detect_language(self, featurefile_contents: str):
        """Detect the specified language in the first line of the Feature File

        If no language code is detected ``en`` is used.
        If an unknown language code is detected an error is raised.
        """

        def __get_language_spec(code):
            language_spec_path = (
                Path(__file__).parent / "languages" / "{}.json".format(code)
            )
            if not language_spec_path.exists():
                raise RadishLanguageNotFound(code)

            with open(
                str(language_spec_path), "r", encoding="utf-8"
            ) as language_spec_file:
                keywords = json.load(language_spec_file)

            return LanguageSpec(code, keywords)

        match = re.match(
            r"^#\s*language:\s*(?P<code>[a-zA-Z-]{2,})", featurefile_contents.lstrip()
        )
        language_code = match.groupdict()["code"] if match else "en"
        return __get_language_spec(language_code)

    def _resolve_preconditions(self, features_rootdir, ast, visited_features):
        for scenario in (s for rules in ast.rules for s in rules.scenarios):
            preconditions = []
            for precondition_tag in (
                t for t in scenario.tags if isinstance(t, PreconditionTag)
            ):
                precondition_path = features_rootdir / precondition_tag.feature_filename

                if precondition_path not in visited_features:
                    precondition_ast = self.parse_file(precondition_path)
                    visited_features[precondition_ast.path] = precondition_ast
                    self._resolve_preconditions(
                        features_rootdir, precondition_ast, visited_features
                    )
                else:
                    precondition_ast = visited_features[precondition_path]

                precondition_scenarios = (
                    s for rules in precondition_ast.rules for s in rules.scenarios
                )
                for precondition_scenario in precondition_scenarios:
                    if (
                        precondition_scenario.short_description
                        == precondition_tag.scenario_short_description
                    ):
                        break
                else:
                    raise RadishPreconditionScenarioDoesNotExist(
                        precondition_path,
                        precondition_tag.scenario_short_description,
                        (
                            s.short_description
                            for rules in ast.rules
                            for s in rules.scenarios
                        ),
                    )

                # check if the precondition leads to a recursion
                if (
                    precondition_scenario in preconditions
                    or precondition_scenario == scenario
                ):
                    raise RadishPreconditionScenarioRecursion(
                        scenario, precondition_scenario
                    )

                preconditions.append(precondition_scenario)

            # assign preconditions
            scenario.set_preconditions(preconditions)
