.. _argumentexpressions:

Argument Expressions
====================

Argument Expressions are an advanced way to specify how your steps should look like.
For the Argument Expressions radish provides an object called *ArgumentExpression*.
To initialize such an object you have to pass a valid format specification which is defined here: https://github.com/r1chardj0n3s/parse#format-specification

Define own expressions
----------------------

Radish provides a simple way to define your own expression formats.
These you can then used in your step definition expressions.

**For example:**
Assume you want to get directly an *User* object in your step definition method as argument instead of the plain username.

Your feature file looks like:

.. code-block:: cucumber

   Feature: Test user database
       I want to test the user database
       from your cool project

       Scenario: Test getting the users
           Given I have the users
               | Cuck Norries | male   | chuck.norries@god.com      |
               | Bruce Wayne  | male   | batman@gotham.com          |
               | Gwen Stacy   | female | girl_from@spiderman.com    |
           When I add them to the database
           Then I expect the user Bruce Wayne has the email batman@gotham.com

For the step *I expect the user ... has the email* I want to get the user as User object and not as plain string.
Radish provides yet another decorator called *arg_expr* which takes a *name* and a Regular Expression as argument.
The function which is decorated by the *arg_expr* will be called for every format with the *arg_expr name* and the return value will be given to the step definition function instead of the matched text.

Register your own expression:

.. code-block:: python

   # -*- coding: utf-8 -*-
   from radish import arg_expr

   @arg_expr("User", r"[A-Z][a-z]+ [A-Z][a-z]+")
   def user_argument_expression(text):
       """
           Return a user object by the given name
       """
       if text not in world.database.users:  # no user found
           return None

       return world.database.users[text]


Your step definition can now use this Argument Expression format:

.. code-block:: python

   # -*- coding: utf-8 -*-
   from radish import then, ArgumentExpression

   @then(ArgumentExpression("I expect the user {user:User} has the email {}"))
   def expect_user_has_email(step, user, expected_email):
       assert user.email == expected_email, "User has email '{}'. Expected was email '{}'".format(user.email, expected_email)
