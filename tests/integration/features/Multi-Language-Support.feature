Feature: Support German as a gherkin language
    In order to write business features
    in the business language Radish shall
    support multiple languages.

    Scenario: Feature in German
        Given the Feature File "german.feature"
            """
            # language: de
            Funktionalität: Funktionalität in Deutsch

                Szenario: Ein einfaches Szenario
                    Gegeben sei ein Schritt
                    Wenn irgendetwas getan wird
                    Dann soll sich etwas verändern
            """
        And the base dir module "steps.py"
            """
            from radish import given, when, then

            @given("sei ein Schritt")
            def gegeben(step):
                step.context.number = 1

            @when("irgendetwas getan wird")
            def wenn(step):
                step.context.number += 1


            @then("soll sich etwas verändern")
            def dann(step):
                assert step.context.number == 2
            """
        When the "german.feature" is run with the options "--no-ansi --no-step-rewrites"
        Then the exit code should be 0
        And the output to match:
            """
            Funktionalität: Funktionalität in Deutsch
                Szenario: Ein einfaches Szenario
                    Gegeben sei ein Schritt
                    Wenn irgendetwas getan wird
                    Dann soll sich etwas verändern

            1 Feature \(1 passed\)
            1 Scenario \(1 passed\)
            3 Steps \(3 passed\)
            """
