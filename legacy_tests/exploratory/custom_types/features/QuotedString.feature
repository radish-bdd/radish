Feature: Support custom type for quoted strings out of the box
    I want to be able to parse double quoted strings
    out of the box with radish.

    Scenario: Parse double quoted strings
        Given I have the string "hodor"
        When I capitalize this string
        Then I expect the string to be "Hodor"

    Scenario: Parse double quoted string with escaping
        Given I have the string "hodor says \"hodor\""
        When I capitalize this string
        Then I expect the string to be "Hodor says \"hodor\""
