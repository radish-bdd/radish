"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import copy

from radish.models.scenario import Scenario


class ScenarioLoop(Scenario):
    """Represents a single instance of a Gherkin Scenario Loop"""

    def __init__(
        self,
        scenario_id: int,
        keyword: str,
        short_description: str,
        tags,
        path: str,
        line: int,
        steps,
        iterations,
    ) -> None:
        super().__init__(
            scenario_id, keyword, short_description, tags, path, line, steps
        )
        self.iterations = iterations
        self.examples = self._build_examples(self.iterations)

    def __repr__(self) -> str:
        return (
            "<ScenarioLoop: '{short_description} with "
            "{iterations} Iterations @ {path}:{line}>".format(
                short_description=self.short_description,
                iterations=self.iterations,
                path=self.path,
                line=self.line,
            )
        )  # pragma: no cover

    def set_feature(self, feature):
        """Set the Feature for this Scenario"""
        super().set_feature(feature)
        for example in self.examples:
            example.set_feature(feature)
            example.keyword = feature.language_spec.keywords["Scenario"]

    def set_background(self, background):
        super().set_background(background)
        for example in self.examples:
            example.set_background(self.background)

    def set_rule(self, rule):
        """Set the Rule for this Scenario"""
        super().set_rule(rule)
        for example in self.examples:
            example.set_rule(rule)

    def _build_examples(self, iterations):
        """Build the examples from the number of Iterations"""
        examples = []
        for example_id in range(1, iterations + 1):
            # Example description
            short_description = "{} [Iteration: {}]".format(
                self.short_description, example_id
            )
            # copy Steps from Scenario Loop for Examples
            steps = copy.deepcopy(self.steps)
            example = Scenario(
                self.id + example_id,
                "Scenario",  # NOTE(TF): keyword will be patched in ``set_feature()``
                short_description,
                self.tags,
                self.path,
                self.line,  # FIXME(TF): use correct line number
                steps,
            )
            examples.append(example)

        return examples

    def has_to_run(self, tag_expression, scenario_ids):
        """Evaluate if this Scenario has to run or not

        The Scenario needs to be run if any of the following conditions is True:
        * No ``tag_expression`` is given
        * The ``tag_expression`` evaluates to True on the Scenario Tags
        * The ``tag_expression`` evaluates to True on the Feature Tags
        * No ``scenario_ids`` is given
        * The ``scenario_ids`` is given and contains this Scenarios Id
        """
        has_to_run_tag_expression = True
        has_to_run_scenario_ids = True

        if tag_expression:
            tag_names = [t.name for t in self.tags + self.feature.tags]
            has_to_run_tag_expression = tag_expression.evaluate(tag_names)

        if scenario_ids:
            has_to_run_scenario_ids = (
                bool({e.id for e in self.examples} & set(scenario_ids))
                or self.id in scenario_ids  # noqa
            )

        if tag_expression and scenario_ids:
            return has_to_run_tag_expression and has_to_run_scenario_ids
        elif tag_expression:
            return has_to_run_tag_expression
        elif scenario_ids:
            return has_to_run_scenario_ids
        else:
            return True
