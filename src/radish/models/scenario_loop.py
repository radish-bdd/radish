import copy

from radish.models.scenario import Scenario


class ScenarioLoop(Scenario):
    """Represents a single instance of a Gherkin Scenario Loop"""

    def __init__(
        self,
        scenario_id: int,
        short_description: str,
        tags,
        path: str,
        line: int,
        steps,
        iterations,
    ) -> None:
        super().__init__(scenario_id, short_description, tags, path, line, steps)
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
        )

    def set_background(self, background):
        super().set_background(background)
        for example in self.examples:
            example.set_background(self.background)

    def _build_examples(self, iterations):
        """Build the examples from the number of Iterations"""
        examples = []
        for example_id in range(1, iterations + 1):
            # copy Steps from Scenario Loop for Examples
            steps = copy.deepcopy(self.steps)
            example = Scenario(
                self.id + example_id,
                # FIXME(TF): add example data to description [foo=bar, bla=df]
                self.short_description,
                self.tags,
                self.path,
                self.line,  # FIXME(TF): use correct line number
                steps,
            )
            examples.append(example)

        return examples
