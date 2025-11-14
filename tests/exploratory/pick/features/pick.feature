Feature: Verify the pick feature
    
    Scenario: Add a method to the world using pick
        Given I don't have a pick decorated method
        Then I expect the pick step not to be in the world
        Given I have a method decorated with pick
        Then I expect the pick step to be in the world
        When I call the pick decorated method
        Then I expect the pick result to be 42

