Feature: Test dividing numbers
    In order to test the
    Scenario Outline features of
    radish I test dividing numbers.

    Scenario Outline: Divide Numbers
        Given I have the number <number1>
        And I have the text
            """
            foobar
            """
        When I add them
        Then I expect the result to be <result>

    Examples:
        | number1 | result |
        | 10      | foo    |
        | 6       | bar    |
        | 24      | foobar |
