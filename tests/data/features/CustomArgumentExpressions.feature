Feature: Custom Argument Expressions
    In order to have beautiful step regex
    I have to test the custom argument expressions

    Scenario: Test Number expressions
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7

    Scenario: Test Math expressions
        Given I have the numeric expression 5 + 15 - 2 * 6
        When I add 10/2 to this
        Then I expect the result to be 13

    Scenario: Float Numbers
        Given I have the float number 5.3
        When I add to my float number -1.5
        Then I expect the float result to be +3.8
