Feature: Test dividing numbers
  with using the step text in to test the
  Scenario Outline features of
  radish I test dividing numbers.

  Scenario Outline: Divide Numbers
    Given I have following numbers
    """
      n1:<number1>,
      n2:<number2>
    """
    When I divide them
    Then I expect the result
    """
      result:<result>
    """

  Examples:
      | number1 | number2 | result |
      | 10      | 2       | 5      |
      | 6       | 3       | 2      |
      | 24      | 8       | 3      |

