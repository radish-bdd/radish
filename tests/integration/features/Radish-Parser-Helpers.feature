Feature: Expose the Radish Parser via cli
    In order to debug and inspect the
    radish AST radish provides a CLI
    to pretty print the AST of parsed
    Feature Files.

    Scenario: Print the AST of a simple single Scenario Feature File
        Given the Feature File "some.feature"
            """
            Feature: Some Feature

                Scenario: Some Scenario
                    When the setup is done
                    Then the setup has been done
            """
        When the "some.feature" is parsed
        Then the output to match:
            """
            start
              feature
                Feature
                Some Feature
                feature_body
                  description
                  scenario
                    Scenario
                    Some Scenario
                    step
                      When
                      the setup is done
                      step_arguments
                    step
                      Then
                      the setup has been done
                      step_arguments
            """
