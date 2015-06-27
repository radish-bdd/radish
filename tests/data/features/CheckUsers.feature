Feature: Check users
    I order to guarantee the backends user system
    the insertion and selection of the users is tested.

    @precondition(SetupDatabase.feature: Setup database and insert default values)
    Scenario: Check users
        When I add the user "Timo furrer"
        Then I expect the user "Timo Furrer" in the database
