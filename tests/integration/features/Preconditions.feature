Feature: Test the radish @precondition feature
    In order to minimize duplicate setup code
    radish supports Preconditions for
    dedicated Scenarios in a Feature.

    Scenario: Use single Precondition Scenario from another Feature File
        Given the Feature File "base.feature"
            """
            Feature: Base Feature for other Features

                Scenario: Setup the database
                    Given the database is running
            """
        And the Feature File "precondition.feature"
            """
            Feature: User of a Precondition

                @precondition(base.feature: Setup the database)
                Scenario: Add user to database
                    When the users are added to the database
                        | barry |
                        | kara  |
                    Then the database should have 2 users
            """
        And the base dir module "steps.py"
            """
            from radish import given, when, then

            @given("the database is running")
            def db_running(step):
                step.context.db_running = True


            @when("the users are added to the database")
            def user_add(step):
                assert step.context.db_running, "DB not running"

                step.context.users = step.data_table


            @then("the database should have {:int} users")
            def expect_users(step, amount_users):
                assert len(step.context.users) == amount_users
            """
        When the "precondition.feature" is run
        Then the exit code should be 0

    Scenario: Use multiple Precondition Scenarios from another Feature File
        Given the Feature File "base.feature"
            """
            Feature: Base Feature for other Features

                Scenario: Setup the first database
                    Given the first database is running

                Scenario: Setup the second database
                    Given the second database is running
            """
        And the Feature File "precondition.feature"
            """
            Feature: User of a Precondition

                @precondition(base.feature: Setup the first database)
                @precondition(base.feature: Setup the second database)
                Scenario: Add user to database
                    When the users are added to the first database
                        | barry |
                        | kara  |
                    And the users are added to the second database
                        | barry |
                        | kara  |
                    Then the first database should have 2 users
                    And the second database should have 2 users
            """
        And the base dir module "steps.py"
            """
            from radish import before, given, when, then

            @before.each_scenario()
            def setup_db_dict(scenario):
                scenario.context.dbs = {}


            @given("the {:word} database is running")
            def db_running(step, db_name):
                step.context.dbs[db_name] = True


            @when("the users are added to the {:word} database")
            def user_add(step, db_name):
                assert step.context.dbs[db_name], "DB not running"
                step.context.dbs[db_name] = step.data_table


            @then("the {:word} database should have {:int} users")
            def expect_users(step, db_name, amount_users):
                assert len(step.context.dbs[db_name]) == amount_users
            """
        When the "precondition.feature" is run
        Then the exit code should be 0

    Scenario: Use Precondition Scenario from the same Feature File when it's defined above
        Given the Feature File "precondition.feature"
            """
            Feature: User of a Precondition

                Scenario: Setup the database
                    Given the database is running

                @precondition(precondition.feature: Setup the database)
                Scenario: Add user to database
                    When the users are added to the database
                        | barry |
                        | kara  |
                    Then the database should have 2 users
            """
        And the base dir module "steps.py"
            """
            from radish import given, when, then

            @given("the database is running")
            def db_running(step):
                step.context.db_running = True


            @when("the users are added to the database")
            def user_add(step):
                assert step.context.db_running, "DB not running"

                step.context.users = step.data_table


            @then("the database should have {:int} users")
            def expect_users(step, amount_users):
                assert len(step.context.users) == amount_users
            """
        When the "precondition.feature" is run
        Then the exit code should be 0

    Scenario: Use Precondition Scenario from the same Feature File when it's defined below
        Given the Feature File "precondition.feature"
            """
            Feature: User of a Precondition

                @precondition(precondition.feature: Setup the database)
                Scenario: Add user to database
                    When the users are added to the database
                        | barry |
                        | kara  |
                    Then the database should have 2 users

                Scenario: Setup the database
                    Given the database is running
            """
        And the base dir module "steps.py"
            """
            from radish import given, when, then

            @given("the database is running")
            def db_running(step):
                step.context.db_running = True


            @when("the users are added to the database")
            def user_add(step):
                assert step.context.db_running, "DB not running"

                step.context.users = step.data_table


            @then("the database should have {:int} users")
            def expect_users(step, amount_users):
                assert len(step.context.users) == amount_users
            """
        When the "precondition.feature" is run
        Then the exit code should be 0

    Scenario: Recursions in Precondition Scenarios should be detected
        Given the Feature File "precondition.feature"
            """
            Feature: User of a Precondition

                @precondition(precondition.feature: Add user to database)
                Scenario: Add user to database
                    When the users are added to the database
                        | barry |
                        | kara  |
                    Then the database should have 2 users
            """
        And the base dir module "steps.py"
            """
            from radish import given, when, then

            @given("the database is running")
            def db_running(step):
                step.context.db_running = True


            @when("the users are added to the database")
            def user_add(step):
                assert step.context.db_running, "DB not running"

                step.context.users = step.data_table


            @then("the database should have {:int} users")
            def expect_users(step, amount_users):
                assert len(step.context.users) == amount_users
            """
        When the "precondition.feature" is run
        Then the run should fail with
            """
            Detected a Precondition Recursion in 'Add user to database' caused by 'Add user to database'
            """
