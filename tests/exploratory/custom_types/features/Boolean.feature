Feature: Support custom type for booleans
    I want to be able to parse boolean values
    out of the box with radish.

    Scenario Outline: Parse true values
        When I have the value <boolean>
        Then I expect it to be parsed as True

    Examples:
            | boolean |
            | 1       |
            | y       |
            | Y       |
            | yes     |
            | Yes     |
            | YES     |
            | true    |
            | True    |
            | TRUE    |
            | on      |
            | On      |
            | ON      |

    Scenario Outline: Parse false values
        When I have the value <boolean>
        Then I expect it to be parsed as False

    Examples:
            | boolean |
            | 0       |
            | n       |
            | N       |
            | no      |
            | No      |
            | NO      |
            | false   |
            | False   |
            | FALSE   |
            | off     |
            | Off     |
            | OFF     |
