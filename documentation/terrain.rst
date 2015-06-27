Terrain
=======

Sometimes it is useful to store some data across features and have :ref:`hooks`.
For this it's common to write a separate module called *terrain.py* next to the *steps.py*.

The terrain module from radish itself provides you a thread specific context object called world.
You can use this object to store your data, objects or what ever you want.
You just have to import the *world* object from the *radish* package.

For example your terrain could look like:

  .. code-block:: python

     # -*- coding: utf-8 -*-
     from radish import before, after, world


     @before.all
     def open_connections(features, marker):
         """
             Open connection to the backend
         """
         world.connection = Connection(host="localhost")
         world.connection.init()


     @after.all
     def close_connections(features, marker):
         """
             Close connection to the backend
         """
         if world.connection:
             world.connection.close()


The available hooks are described in detail at :ref:`hooks`.


Add method to the world object
------------------------------

Radish provides a decorator to add a function to the world object.
This could be very useful it your hooks are split up to separate modules and you want to access a function defined in one
hook module from another module with hooks.


  .. code-block:: python

     # -*- coding: utf-8 -*-
     from radish import before, world


     @world.pick
     def send_data(user, data):
         """
             Send data to a specific user
         """
         assert world.connection, "No connection initialized"
         assert user not in world.users, "User {} not found".format(user)
         assert data, "No data given to send to {}".format(user)
         world.connection.send(world.users[user].token, data)


And in one of your step definition you can use this method:

  .. code-block:: python

     # -*- coding: utf-8 -*-
     from radish.stepregistry import when
     from radish import world, ArgumentExpression

     @when(ArgumentExpression("I send '{}' to the user {}"))
     def send_data_to_user(step, data, user):
         world.send_data(user, data)
