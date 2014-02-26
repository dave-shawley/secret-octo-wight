HTTP API
========

This application exposes the Family Tree objects as HTTP resources using
a standard RESTful approach.  The canonical representation for objects is
a JSON document (fully described in `Representations`_).  This section
describes the HTTP API itself in terms of resources and actions.  The API
itself is built on top of `Hypermedia as the Engine of Application State`_
as a core concept.  Therefore, each of the representations contain a list
of available actions with descriptive names.

**Notes about this section**

* This section only describes the entry points into the application since
  these are the only URLs that you actually need to use.
* For resources that accept a representation, only the required fields
  are documented.  See the :ref:`Representations` section for a full
  description of the available fields and the :ref:`Python Models` section
  for a description of each entity in the information model.


Creating a Person
-----------------
.. autotornado:: familytree.main:application
   :endpoints: CreatePersonHandler.post


.. _Representations:

Representations
===============
Each representation includes a list of the currently available actions for
the entity.  The list of actions is consistently included as an embedded
dictionary named ``actions`` where the key is the action name and the value
is another dictionary that describes how to *invoke* the action.  The
representation also includes a ``self`` attribute at the top-level that
contains the canonical resource name for the representation.  An example
should clear up my dense verbiage.

.. code-block:: yaml

   ---
   self: http://some.endpoint/resource/path
   display_name: Marilyn vos Savant
   actions:
     delete-person:
       method: DELETE
       url: http://some.url

.. _person_representation:

Person
------
A *Person* is the leaf in a family tree.  They are created by submitting
a representation as described in `Creating a Person`_.

+-----------------+---------------------------------------------------+
| Action          | Description                                       |
+=================+===================================================+
| delete-person   | Remove this person from the set of objects        |
+-----------------+---------------------------------------------------+

Example
~~~~~~~

.. code-block:: json

   {
      "self": "http://some.endpoint/resource/path",
      "displayName": "Marilyn vos Savant",
      "actions": {
         "deletePerson": {
            "method": "DELETE",
            "url": "http://some.url"
         }
      }
   }

.. _Hypermedia as the Engine of Application State: http://www.wikipedia.org/wiki/HATEOS
