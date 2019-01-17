Feature: Feature with unicode all over 🐢 and 🐧
    Radish shall support unicode

    Background: A simple Background with 🐢 and 🐧
        Given I have the number 5
        And I have the number 3

    Scenario: Scenario with multiple Steps with 🐢 and 🐧
        Given I have a Step with 🐢 and 🐧
        When I do something
        Then I expect something

    Scenario Outline: A Scenario Outline 🐢 and 🐧
        Given I have the number <x> 🐢 and 🐧
        And I have the number <y>
        When I add them up
        Then I expect the sum to be <z>

    Examples:
        # notice the added numbers in the background, too
        | x | y | z  |
        | 1 | 2 | 11 |
        | 4 | 5 | 17 |

    Scenario Loop 2: This is a looped Scenario 🐢 and 🐧
        Given I have an instable function 🐢 and 🐧
        When I execute it
        Then I expect it to pass
