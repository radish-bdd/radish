@Foo
Feature: Test summing numbers
  In order to test the basic
  features of radish I test
  to sum numbers.

  @FooBar
  @author tuxtimo @reviewer l33tname @date Sun, 26 Feb 2023 17:52:52 +0100 @requirements 1,2
  Scenario: Sum two numbers
    Given I have the number 5
      And I have the number 3
    When I sum them
    Then I expect the result to be 8

  @author(tuxtimo) @reviewer(l33tname) @date(Sun, 26 Feb 2023 17:52:52 +0100) @requirements(1,2)
  Scenario: Sum three numbers
    Given I have the number 5
      And I have the number 3
      And I have the number 2
    When I sum them
    Then I expect the result to be 10
