"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import copy

from radish.models.scenario import Scenario


class ScenarioOutline(Scenario):
    """Represents a single instance of a Gherkin Scenario Outline"""

    def __init__(
        self,
        scenario_id: int,
        short_description: str,
        tags,
        path: str,
        line: int,
        steps,
        examples_table,
    ) -> None:
        super().__init__(scenario_id, short_description, tags, path, line, steps)
        self.examples_table = examples_table
        self.examples = self._build_examples(self.examples_table)

    def __repr__(self) -> str:
        return (
            "<ScenarioOutline: '{short_description} with "
            "{examples} Examples @ {path}:{line}>".format(
                short_description=self.short_description,
                examples=len(self.examples_table),
                path=self.path,
                line=self.line,
            )
        )

    def set_feature(self, feature):
        """Set the Feature for this Scenario"""
        super().set_feature(feature)
        for example in self.examples:
            example.set_feature(feature)

    def set_background(self, background):
        super().set_background(background)
        for example in self.examples:
            example.set_background(self.background)

    def set_rule(self, rule):
        """Set the Rule for this Scenario"""
        super().set_rule(rule)
        for example in self.examples:
            example.set_rule(rule)

    def _build_examples(self, examples_table):
        """Build the examples from the Examples Table"""
        examples = []
        for example_id, example_decl in enumerate(examples_table, start=1):
            # patch Steps from Scenario Outline for Examples
            steps = copy.deepcopy(self.steps)

            # Example description
            example_short_description_data = [
                "{}: {}".format(k, v)
                for k, v
                in example_decl.items()
            ]
            short_description = "{} [{}]".format(
                self.short_description, ", ".join(example_short_description_data))

            for step in steps:
                for example_key, example_value in example_decl.items():
                    step.text = step.text.replace(
                        "<{}>".format(example_key), example_value
                    )

            example = Scenario(
                self.id + example_id,
                short_description,
                self.tags,
                self.path,
                self.line,  # FIXME(TF): use correct line number
                steps,
            )
            examples.append(example)

        return examples
