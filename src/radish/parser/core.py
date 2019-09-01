"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from pathlib import Path

from lark import Lark, UnexpectedInput

from radish.parser.errors import (
    RadishMisplacedBackground,
    RadishMissingFeatureShortDescription,
    RadishMissingRuleShortDescription,
    RadishMissingScenarioShortDescription,
    RadishMultipleBackgrounds,
    RadishPreconditionScenarioDoesNotExist,
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
from radish.parser.transformer import RadishGherkinTransformer
from radish.models import PreconditionTag


class FeatureFileParser:
    """Radish Feature File Parser responsible to parse a single Feature File"""

    def __init__(
        self, grammerfile: Path = None, resolve_preconditions: bool = True
    ) -> None:
        if grammerfile is None:
            grammerfile = Path(__file__).parent / "grammer.g"

        self.grammerfile = grammerfile
        self.resolve_preconditions = resolve_preconditions

        self._transformer = RadishGherkinTransformer()
        self._parser = Lark.open(
            str(grammerfile), parser="lalr", transformer=self._transformer
        )
        self._current_feature_id = 1

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
        # prepare the transformer for the Feature File
        self._transformer.prepare(featurefile_path, featurefile_contents, feature_id)

        try:
            ast = self._parser.parse(featurefile_contents)
        except UnexpectedInput as exc:
            exc_class = exc.match_examples(
                self._parser.parse,
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
                    ):  # noqa
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

                preconditions.append(precondition_scenario)

            # assign preconditions
            scenario.set_preconditions(preconditions)
