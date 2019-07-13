"""
This module contains the core components for the radish Gherkin Parser
"""

from pathlib import Path

from lark import Lark, UnexpectedInput

from radish.parser.errors import (
    RadishMisplacedBackground,
    RadishMissingFeatureShortDescription,
    RadishMissingRuleShortDescription,
    RadishMissingScenarioShortDescription,
    RadishMultipleBackgrounds,
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


class FeatureFileParser:
    def __init__(self, grammerfile: Path = None) -> None:
        if grammerfile is None:
            grammerfile = Path(__file__).parent / "grammer.g"

        self.grammerfile = grammerfile

        self._transformer = RadishGherkinTransformer()
        self._parser = Lark.open(
            str(grammerfile), parser="lalr", transformer=self._transformer
        )
        self._current_feature_id = 1

    def parse_file(self, featurefile: Path):
        """Parse the given Feature File using the parser"""
        with open(str(featurefile), "r", encoding="utf-8") as featurefile_f:
            contents = featurefile_f.read()
            return self.parse_contents(featurefile, contents)

    def parse_contents(self, featurefile_path: Path, featurefile_contents: str):
        # prepare the transformer for the Feature File
        self._transformer.prepare(
            featurefile_path, featurefile_contents, self._current_feature_id
        )

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
