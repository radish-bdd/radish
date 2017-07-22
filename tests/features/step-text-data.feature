Feature: Step Text Data
    Radish shall support Step Text Data

    Scenario: A Step with Text
        Given I have the following quote
            """
            To be or not to be
            """
        When I look for it's author
        Then I will find Shakespeare
