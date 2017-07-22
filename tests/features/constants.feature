@constant(SomeNumber: 5)
Feature: Test summing numbers
  In order to test the constant
  features of radish I test
  to sum numbers.

  @constant(ExpectedResult: 8)
  Scenario: Sum two numbers
    Given I have the number ${SomeNumber}
      And I have the number 3
    When I add them up
    Then I expect the sum to be ${ExpectedResult}

  @constant(ExpectedResult: 10)
  Scenario: Sum three numbers
    Given I have the number ${SomeNumber}
      And I have the number 3
      And I have the number 2
    When I add them up
    Then I expect the sum to be ${ExpectedResult}
