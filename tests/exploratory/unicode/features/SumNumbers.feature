Feature: Test summing numbers
  In order to test the basic
  features of radish I test
  to sum numbers.

  Scenario: Sum two numbers
    Given I have the number 5
      And I have the number 3
    When I sum them 🎉
    Then I expect the result to be 8

  Scenario: Sum three numbers
    Given I have the number 5
      And I have the number 3
      And I have the number 2
    When I sum them 🎉
    Then I expect the result to be 10
