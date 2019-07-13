class Rule:
    """Represents a single instance of a Gherkin Rule"""

    def __init__(self, short_description, path: str, line: int, scenarios) -> None:
        self.short_description = short_description
        self.path = path
        self.line = line
        self.scenarios = scenarios

    def set_background(self, background):
        """Set the Background for all Scenarios in this Rule"""
        for scenario in self.scenarios:
            scenario.set_background(background)

    def __repr__(self) -> str:
        return "<Rule: '{short_description}' with {scenarios} Scenarios @ {path}:{line}>".format(
            short_description=self.short_description,
            scenarios=len(self.scenarios),
            path=self.path,
            line=self.line,
        )


class DefaultRule(Rule):
    """Represents the default Rule which is used if no rule is specified"""

    def __init__(self, path: str, line: int, scenarios) -> None:
        super().__init__(None, path, line, scenarios)

    def __repr__(self) -> str:
        return "<DefaultRule: with {scenarios} Scenarios @ {path}:{line}>".format(
            scenarios=len(self.scenarios), path=self.path, line=self.line
        )
