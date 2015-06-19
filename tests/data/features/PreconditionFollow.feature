Feature: Insert users
    In order to demonstrate the scenario precondition
    I write this base to setup the database

    @precondition(PreconditionBase.feature: Setup user database)
    Scenario: Insert default users
        I add the users
            | Timo     | Furrer  | tuxtimo@gmail.com |

