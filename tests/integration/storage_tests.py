import sys
import unittest

import fluenttest
import mock

from familytree import storage


###############################################################################
### ModelInstance.as_dictionary
###############################################################################

class WhenConvertingModelInstanceToDictionary(
        fluenttest.TestCase, unittest.TestCase):

    allowed_exceptions = Exception

    @classmethod
    def arrange(cls):
        super(WhenConvertingModelInstanceToDictionary, cls).arrange()
        cls.instance = storage.ModelInstance()

    @classmethod
    def act(cls):
        cls.instance.as_dictionary()

    def should_raise_not_implemented(self):
        self.assertIsInstance(self.exception, NotImplementedError)


###############################################################################
### ModelInstance.from_dictionary
###############################################################################


class WhenCreatingInstanceFromDictionary(
        fluenttest.TestCase, unittest.TestCase):

    allowed_exceptions = Exception

    @classmethod
    def act(cls):
        storage.ModelInstance.from_dictionary({})

    def should_raise_not_implemented(self):
        self.assertIsInstance(self.exception, NotImplementedError)


###############################################################################
### get_item
###############################################################################

class WhenGettingItem(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(WhenGettingItem, cls).arrange()
        cls.storage_layer = cls.patch('familytree.storage._STORAGE')
        cls.storage_type = mock.MagicMock()

    @classmethod
    def act(cls):
        cls.item = storage.get_item(cls.storage_type, mock.sentinel.item_id)

    def should_retrieve_item_by_key(self):
        self.storage_layer.__getitem__.assert_called_once_with(
            (str(self.storage_type), mock.sentinel.item_id))

    def should_create_item_from_dict_repr(self):
        self.storage_type.from_dictionary.assert_called_once_with(
            self.storage_layer.__getitem__.return_value)

    def should_return_created_item(self):
        self.assertIs(
            self.item, self.storage_type.from_dictionary.return_value)


class WhenGettingItemThatDoesNotExist(fluenttest.TestCase, unittest.TestCase):
    allowed_exceptions = Exception

    @classmethod
    def arrange(cls):
        super(WhenGettingItemThatDoesNotExist, cls).arrange()
        cls.storage_layer = cls.patch('familytree.storage._STORAGE')
        cls.storage_layer.__getitem__.side_effect = KeyError
        cls.storage_type = mock.Mock()

    @classmethod
    def act(cls):
        storage.get_item(cls.storage_type, mock.sentinel.item_id)

    def should_raise_instance_not_found(self):
        self.assertIsInstance(self.exception, storage.InstanceNotFound)

    def should_include_model_instance_class_in_exception(self):
        self.assertEqual(self.exception.model_class, self.storage_type)

    def should_include_instance_id_in_exception(self):
        self.assertEqual(self.exception.instance_id, mock.sentinel.item_id)


###############################################################################
### save_item
###############################################################################

class WhenSavingItem(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(WhenSavingItem, cls).arrange()
        cls.storage_layer = cls.patch('familytree.storage._STORAGE')
        cls.item = mock.Mock()

    @classmethod
    def act(cls):
        storage.save_item(cls.item, mock.sentinel.item_id)

    def should_convert_item_to_dictionary(self):
        self.item.as_dictionary.assert_called_once_with()

    def should_save_item(self):
        self.storage_layer.__setitem__.assert_called_once_with(
            (str(self.item.__class__), mock.sentinel.item_id),
            self.item.as_dictionary.return_value,
        )
