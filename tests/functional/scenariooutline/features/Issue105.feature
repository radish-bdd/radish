Feature: Test dividing numbers
  In order to test the
  Scenario Outline features of
  radish I test dividing numbers.

  @bar
  Scenario Outline: Divide Numbers
    Given I have the number <number1>
      And I have the number <number2>
    When I divide them
    Then I expect the result to be <result>

  Examples:
      | number1 | number2 | result |
      | 10      | 2       | 5      |
      | 6       | 3       | 2      |
      | 24      | 8       | 3      |

  @foo
  Scenario: Divide Numbers with Tag
    Given I have the number 10
      And I have the number 2
    When I divide them
    Then I expect the result to be 5
