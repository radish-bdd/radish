Feature: Step Tabular Data
    Radish shall support tubular data
    for a specific step

    Scenario: Tabular Data for a Step
        Given I have the following heros
            | firstname | surname | heroname |
            | Bruce     | Wayne   | Batman    |
            | Peter     | Parker  | Spiderman |
        When I capitalize their first name
        Then I have the following names
            | cap_heroname |
            | BRUCE        |
            | PETER        |
