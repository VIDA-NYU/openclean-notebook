# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the openclean API extensions of the openclean engine."""

from openclean_jupyter.engine import DB, Namespace


def test_edit_dataset(dataset, tmpdir):
    """Test to ensure that we can call the edit function without an error."""
    engine = DB(str(tmpdir))
    engine.create(source=dataset, name='DS', primary_key='A')
    engine.edit('DS')
    engine.edit('DS', n=1)


def test_init_namespaces():
    """Test initialize the set of namespace descriptors."""
    # -- Default has one namespace for string functions --
    namespaces = DB().namespaces
    assert len(namespaces) == 1
    assert set([n.label for n in namespaces.values()]) == set(['Text'])
    # -- The text namespace is added if not in initial set --
    ns = Namespace(identifier='numbers', label='Num')
    namespaces = DB(namespaces=[ns]).namespaces
    assert len(namespaces) == 2
    assert set([n.label for n in namespaces.values()]) == set(['Num', 'Text'])
    # -- If a string namespace is given it will not be replaced ---
    ns = Namespace(identifier='string', label='Num')
    namespaces = DB(namespaces=[ns]).namespaces
    assert len(namespaces) == 1
    assert set([n.label for n in namespaces.values()]) == set(['Num'])
