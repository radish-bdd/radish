Feature: Test steps with multiline text block
    In order to test the step multiline
    text feature I write this feature

    Scenario: Some multiline steps text
        Given I have the following data:
            """
              Some extra data for the step
            """
        When I ignore this step
        Then I expect the data to be "Some extra data for the step"

    Scenario: Some multiline steps text on start line
        Given I have the following data:
            """ Some extra data for the step
            """
        When I ignore this step
        Then I expect the data to be "Some extra data for the step"

    Scenario: Some multiline steps text on end line
        Given I have the following data:
            """
              Some extra data for the step """
        When I ignore this step
        Then I expect the data to be "Some extra data for the step"

    Scenario: Some multiline steps text start and end on same line
        Given I have the following data:
            """ Some extra data for the step """
        When I ignore this step
        Then I expect the data to be "Some extra data for the step"
