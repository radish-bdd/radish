Feature: Support Step Text Matching
    In order to *unit test* the Step Text
    Patterns radish provides tooling
    to match sample Step Texts against
    the Step Patterns from the Step Implementations.

    Scenario: Empty Matcher Config
        Given the Matcher Config File "matcher-config.yml"
            """

            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a Step")
            def given_there_is_a_step(step):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            The matcher config .*?/matcher-config.yml was empty - Nothing to do :\)
            """

    Scenario: Match single Step
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is a Step
              should_match: given_there_is_a_step
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a Step")
            def given_there_is_a_step(step):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_a_step    ✔
            """

    Scenario: Match multiple Steps
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is a Step
              should_match: given_there_is_a_step

            - step: When there is a Step
              should_match: when_there_is_a_step
            """
        And the base dir module "steps.py"
            """
            from radish import given, when

            @given("there is a Step")
            def given_there_is_a_step(step):
                pass


            @when("there is a Step")
            def when_there_is_a_step(step):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_a_step    ✔
            >> STEP 'When there is a Step' SHOULD MATCH when_there_is_a_step    ✔
            """

    Scenario: Fail if Step cannot be matched
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is a Step
              should_match: given_there_is_a_step
            """
        And the base dir module "steps.py"
            """

            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_a_step    ✘[ ]
              - Expected Step Text didn't match any Step Implementation
            """

    Scenario: Fail if Step Text matches wrong Step
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is a Step
              should_match: given_there_is_a_step
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a Step")
            def given_there_is_another_step(step):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_a_step    ✘ \(at .*?:3\)
              - Expected Step Text matched given_there_is_another_step instead of given_there_is_a_step
            """

    Scenario: Show passed and failed matches
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is a Step
              should_match: given_there_is_a_step

            - step: Given there is a Step
              should_match: given_there_is_another_step
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a Step")
            def given_there_is_a_step(step):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_a_step    ✔
            >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_another_step    ✘ \(at .*?:3\)
              - Expected Step Text matched given_there_is_a_step instead of given_there_is_another_step
            """

    Scenario: Match built-in type Step argument
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is a Step with 1 and value
              should_match: given_there_is_a_step
              with_arguments:
                - number: 1
                - string: "value"
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a Step with {:int} and {:word}")
            def given_there_is_a_step(step, number, string):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is a Step with 1 and value' SHOULD MATCH given_there_is_a_step    ✔
            """

    Scenario: Fail to match built-in type Step argument
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is a Step with 1 and value
              should_match: given_there_is_a_step
              with_arguments:
                - number: 0
                - string: "another value"
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a Step with {:int} and {:word}")
            def given_there_is_a_step(step, number, string):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is a Step with 1 and value' SHOULD MATCH given_there_is_a_step    ✘ \(at .*?:3\)
              - Expected argument "number" with value "0" does not match value "1"
              - Expected argument "string" with value "another value" does not match value "value"
            """

    Scenario: Match custom type Step argument using *use_repr*
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is a Step with 42
              should_match: given_there_is_a_step
              with_arguments:
                - custom_type:
                    type: CustomType
                    value: CustomType(42)
                    use_repr: True
            """
        And the base dir module "steps.py"
            """
            from radish import given, custom_type

            class CustomType:
                def __init__(self, number):
                    self.number = number

                def __repr__(self):
                    return "CustomType({})".format(self.number)


            @custom_type("CustomType", "[0-9]+")
            def parse_custom_type(text):
                return CustomType(int(text))


            @given("there is a Step with {:CustomType}")
            def given_there_is_a_step(step, custom_type):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is a Step with 42' SHOULD MATCH given_there_is_a_step    ✔
            """

    Scenario: Expect single Step not to match
        Given the Matcher Config File "matcher-config.yml"
            """
            - step: Given there is another Step
              should_not_match: given_there_is_a_step
            """
        And the base dir module "steps.py"
            """
            from radish import given

            @given("there is a Step")
            def given_there_is_a_step(step):
                pass
            """
        When the "matcher-config.yml" is tested
        Then the output to match:
            """
            >> STEP 'Given there is another Step' SHOULD NOT MATCH given_there_is_a_step    ✔
            """

    Rule: Coverage Features

        Scenario: Do not show any missing Step Implementations if there are none
            Given the Matcher Config File "matcher-config.yml"
                """

                """
            And the base dir module "steps.py"
                """

                """
            When the "matcher-config.yml" is tested with the options "--show-missing"
            Then the output to match:
                """
                The matcher config .*?/matcher-config.yml was empty - Nothing to do :\)
                Everything is covered!
                """

        Scenario: Show all missing Step Implementations
            Given the Matcher Config File "matcher-config.yml"
                """

                """
            And the base dir module "steps.py"
                """
                from radish import given

                @given("there is a Step")
                def given_there_is_a_step(step):
                    pass
                """
            When the "matcher-config.yml" is tested with the options "--show-missing"
            Then the output to match:
                """
                The matcher config .*?/matcher-config.yml was empty - Nothing to do :\)
                Missing from: .*?/radish/steps.py
                  - given_there_is_a_step:3
                """

        Scenario: Show templates for all missing Step Implementations
            Given the Matcher Config File "matcher-config.yml"
                """

                """
            And the base dir module "steps.py"
                """
                from radish import given

                @given("there is a Step")
                def given_there_is_a_step(step):
                    pass
                """
            When the "matcher-config.yml" is tested with the options "--show-missing-templates"
            Then the output to match:
                """
                The matcher config .*?/matcher-config.yml was empty - Nothing to do :\)
                Missing from: .*?/radish/steps.py
                  - given_there_is_a_step:3

                Add the following to your matcher-config.yml to cover the missing Step Implementations:

                # testing Step Implementation at .*?/radish/steps.py:3
                - step: "<insert sample Step Text here>"
                  should_match: given_there_is_a_step
                """

        Scenario: Show templates for all missing Step Implementations including Step Arguments
            Given the Matcher Config File "matcher-config.yml"
                """

                """
            And the base dir module "steps.py"
                """
                from radish import given

                @given("there is a Step")
                def given_there_is_a_step(step):
                    pass


                @given("there is a numbers {:int} and {second:int}")
                def given_number(step, first, second):
                    pass
                """
            When the "matcher-config.yml" is tested with the options "--show-missing-templates"
            Then the output to match:
                """
                The matcher config .*?/matcher-config.yml was empty - Nothing to do :\)
                Missing from: .*?/radish/steps.py
                  - given_there_is_a_step:3
                  - given_number:8

                Add the following to your matcher-config.yml to cover the missing Step Implementations:

                # testing Step Implementation at .*?/radish/steps.py:3
                - step: "<insert sample Step Text here>"
                  should_match: given_there_is_a_step


                # testing Step Implementation at .*?/radish/steps.py:8
                - step: "<insert sample Step Text here>"
                  should_match: given_number
                  with_arguments:
                    - first: <insert argument value here>
                    - second: <insert argument value here>
                """
