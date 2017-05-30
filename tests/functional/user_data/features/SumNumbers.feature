Feature: Test summing numbers from user data specified on the command-line
  In order to test the basic
  features of radish I test
  to sum numbers.

  Scenario: Sum two numbers from user data command-line arguments
    Given I have the number in user data as X
    And I have the number in user data as Y
    When I sum them
    Then I expect the result to be the value in user data as Z