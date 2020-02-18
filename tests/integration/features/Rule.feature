Feature: Support Rule Blocks
    In order to emphasize Business Rules
    for Scenarios radish shall
    support the Gherkin v6 Rule Blocks

    Scenario: Implicit default Rule
        Given the Feature File "default-rule.feature"
            """
            Feature: Default Rule

                Scenario: This Scenario belongs to the Default Rule
                    Given there is a step
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a step")
            def there_is_a_step(step):
                pass
            """
        When the "default-rule.feature" is run
        Then the exit code should be 0
        And the output to match:
            """
            Feature: Default Rule
                Scenario: This Scenario belongs to the Default Rule
                    Given there is a step
            """

    Scenario: Explicit single Rule
        Given the Feature File "default-rule.feature"
            """
            Feature: Some Feature

                Rule: Some Business Rule

                    Scenario: Some Scenario
                        Given there is a step
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a step")
            def there_is_a_step(step):
                pass
            """
        When the "default-rule.feature" is run
        Then the exit code should be 0
        And the output to match:
            """
            Feature: Some Feature
                Rule: Some Business Rule

                    Scenario: Some Scenario
                        Given there is a step
            """

    Scenario: Explicit multiple Rules
        Given the Feature File "default-rule.feature"
            """
            Feature: Some Feature

                Rule: Some Business Rule

                    Scenario: Some Scenario
                        Given there is a step

                Rule: Another Business Rule

                    Scenario: Some other Scenario
                        Given there is a step
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a step")
            def there_is_a_step(step):
                pass
            """
        When the "default-rule.feature" is run with the options "--no-step-rewrites"
        Then the exit code should be 0
        And the output to match:
            """
            Feature: Some Feature
                Rule: Some Business Rule

                    Scenario: Some Scenario
                        Given there is a step

                Rule: Another Business Rule

                    Scenario: Some other Scenario
                        Given there is a step
            """

    Scenario: Implicit and Explicit Rules
        Given the Feature File "default-rule.feature"
            """
            Feature: Some Feature

                Scenario: Some Scenario
                    Given there is a step

                Rule: Another Business Rule

                    Scenario: Some other Scenario
                        Given there is a step
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a step")
            def there_is_a_step(step):
                pass
            """
        When the "default-rule.feature" is run with the options "--no-step-rewrites"
        Then the exit code should be 0
        And the output to match:
            """
            Feature: Some Feature
                Scenario: Some Scenario
                    Given there is a step

                Rule: Another Business Rule

                    Scenario: Some other Scenario
                        Given there is a step
            """
