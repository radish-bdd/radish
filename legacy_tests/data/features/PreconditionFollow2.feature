Feature: Check users
    In order to demonstrate the scenario precondition
    I write this base to setup the database

    @precondition(PreconditionFollow.feature: Insert default users)
    Scenario: Check users
        Then I expect the user "Timo Furrer" in the database
