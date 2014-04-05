"""Testing compatability layer.

This module insulates the tests from differences in the unittest and
mock modules.  Tests should NEVER directly import either module.
Instead, the following imports should be used::

    from ..helpers.compat import mock
    from ..helpers.compat import unittest

This will ensure that tests will always see the a Python 2.7 compatible
implementation of ``unittest`` and a Python 3 compatible version of
``mock``.

"""
import sys

try:
    from unittest import mock
except ImportError:
    import mock

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

__all__ = (
    'mock',
    'unittest',
)
