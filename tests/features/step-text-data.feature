Feature: Step Text Data
    Radish shall support Step Text Data

    Scenario: A Step with Text
        Given I have the following quote
            """
            To be or not to be
            """
        When I look for it's author
        Then I will find Shakespeare

    Scenario: YAML definition in Step with Text
        When YAML specification is set to
          """
          version: '3'
          services:
            webapp:
              build: ./dir
          """
        Then YAML specification contains proper data

    Scenario: A step with text on endigs
         When YAML specification is set to
            """version: '3'
            services:
              webapp:
                build: ./dir"""
          Then YAML specification contains proper data
