Feature: Test adding quotes to database
  In order to test the step text data
  features of radish I test to add
  users to the database.

  Scenario: Add quotes to the database
    Given I have the following quote
      """
        To be or not to be
      """
    When I add it to the database
    Then I expect 1 quote in the database
