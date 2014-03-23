Python Implementation
=====================

.. _Python Models:

Models
------
.. autoclass:: familytree.person.Person
   :members:


Request Handlers
----------------
.. autoclass:: familytree.handlers.BaseHandler
   :members:

.. autoclass:: familytree.person.CreatePersonHandler
   :members:

.. autoclass:: familytree.person.PersonHandler
   :members:


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
