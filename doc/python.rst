Python Implementation
=====================

.. _Python Models:

Models
------
.. autoclass:: familytree.person.Person
   :members:

.. autoclass:: familytree.event.Event
   :members:


Request Handlers
----------------
.. autoclass:: familytree.handlers.BaseHandler
   :members:
   :exclude-members: delete, get, head, patch, post

.. autoclass:: familytree.event.CreateEventHandler
   :members:
   :exclude-members: delete, get, head, patch, post

.. autoclass:: familytree.event.EventHandler
   :members:
   :exclude-members: delete, get, head, patch, post

.. autoclass:: familytree.person.CreatePersonHandler
   :members:
   :exclude-members: delete, get, head, patch, post

.. autoclass:: familytree.person.PersonHandler
   :members:
   :exclude-members: delete, get, head, patch, post


Storage Layer
-------------
.. automodule:: familytree.storage
   :members:

.. :class:: familytree.storage.ModelInstance
   .. :method:: as_dictionary()
      :rtype: dict
      :returns: a representation of the model instance as a
         dictionary

   .. :classmethod:: from_dictionary(dict_repr)
      :param dict dict_repr: a dictionary returned from the
      :meth:`as_dictionary` instance method

   .. :attribute:: id
      The instance's unique identifier
