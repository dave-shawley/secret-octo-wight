"""Storage Abstraction.

This module implements a storage layer for model instances.  A model
instance is defined as an object that implements the
:class:`ModelInstance` abstraction.  Any class that implements this
abstraction can be saved by calling :func:`save_item` and retrieved
by a call to :func:`get_item`.

"""

_STORAGE = {}


class InstanceNotFound(Exception):
    """Raised when a model instance is not found.

    :param type model_class: the class that was used in the
        lookup
    :param str item_id: the unique identifier that was used in
        the lookup operation

    Both of the parameters are saved as matching attributes.

    """

    def __init__(self, model_class, item_id):
        super(InstanceNotFound, self).__init__(
            'instance of {0} not found with id of {1}'.format(
                model_class, item_id)
        )
        self.model_class = model_class
        self.instance_id = item_id


class ModelInstance:
    """Simple model instance.

    A model instance is any object:

    1. that implements the :meth:`as_dictionary` method
    2. whose class implements a :meth:`from_dictionary` class
       method

    It does not have to have this class in its ``__mro__``.  All
    that is required is the implementation of the two methods such
    that::

        o.__class__.from_dictionary(o.as_dictionary()) == o

    is true for all instances of ``o``.

    """

    def as_dictionary(self):
        """Return a dictionary representation of this object."""
        raise NotImplementedError

    @classmethod
    def from_dictionary(cls, dict_repr):
        """Create a model instance from a dictionary.

        :param dict dict_repr: a dictionary return from calling the
            :meth:`as_dictionary` method on a model instance
        :returns: a model instance

        """
        raise NotImplementedError


def get_item(item_type, item_id):
    """Retrieve an item of a specific type by id.

    :param type item_type: the type of item to retrieve
    :param str item_id: the unique ID of the item to retrieve
    :returns: the model instance identified by ``item_id``
    :raises InstanceNotFound: when no instance exists with ``item_id``

    """
    try:
        dict_repr = _STORAGE[(str(item_type), item_id)]
        return item_type.from_dictionary(dict_repr)
    except KeyError:
        raise InstanceNotFound(item_type, item_id)


def save_item(item, item_id):
    """Save an item to the persistence layer.

    :param ModelInstance item: the item to save
    :param str item_id: the unique identifier associated with ``item``

    """
    dict_repr = item.as_dictionary()
    key = (str(item.__class__), item_id)
    _STORAGE[key] = dict_repr
