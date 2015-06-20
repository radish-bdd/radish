Feature: Check users
    In order to demonstrate the scenario precondition
    I write this base to setup the database

    Scenario: Some normal scenario without preconditions
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7

    @precondition(PreconditionFollow.feature: Insert default users)
    @precondition(PreconditionFollow2.feature: Check users)
    Scenario: Check users 2
        Then I expect the user "Timo Furrer" in the database
