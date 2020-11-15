# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the volatile object store."""

from openclean_jupyter.engine.store.mem import VolatileObjectStore


def test_volatile_object_store():
    """Test all methods of the volatile object store."""
    store = VolatileObjectStore()
    # Accessing non exisitng objects does not raise any errors.
    assert store.read_object('ABC') is None
    assert store.delete_object('ABC') is None
    # Read and write objects.
    store.write_object(key='ABC', value='abc')
    store.write_object(key='XYZ', value='xyz')
    store.commit()
    assert store.read_object('ABC') == 'abc'
    assert store.read_object('XYZ') == 'xyz'
    store.delete_object('ABC')
    assert store.read_object('ABC') is None
    assert store.read_object('XYZ') == 'xyz'
