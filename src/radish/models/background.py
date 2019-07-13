from radish.models.scenario import Scenario


class Background(Scenario):
    """Represents a single instance of a Gherkin Background"""

    def __init__(self, short_description: str, path: str, line: int, steps) -> None:
        super().__init__(0, short_description, None, path, line, steps)

    def __repr__(self) -> str:
        return "<Background: '{short_description} with {steps} Steps @ {path}:{line}>".format(
            short_description=self.short_description,
            steps=len(self.steps),
            path=self.path,
            line=self.line,
        )
