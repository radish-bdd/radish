Feature: Test multiplying numbers
  In order to test the
  Scenario Outline features of
  radish I test multiplying numbers.

  @bar
  Scenario Loop 10: Multiply Numbers
    Given I have the number 6
      And I have the number 7
    When I multiply them
    Then I expect the result to be 42

  @foo
  Scenario: Multiply Numbers again
    Given I have the number 6
      And I have the number 7
    When I multiply them
    Then I expect the result to be 42
