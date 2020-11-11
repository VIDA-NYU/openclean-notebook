# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the basic functionality of the openclean engine."""

import pytest


@pytest.mark.parametrize('cached', [True, False])
def test_create_and_delete_dataset(cached, persistent_engine, dataset):
    """Test creating and deleting datasets via the engine."""
    # Create and checkout a dataset snapshot.
    df = persistent_engine.create(source=dataset, name='My Data')
    assert df.shape == (2, 3)
    df = persistent_engine.checkout(name='My Data')
    assert df.shape == (2, 3)
    # Cannot create multiple datasets with the same name.
    with pytest.raises(ValueError):
        persistent_engine.create(source=dataset, name='My Data')
    # Create a second dataset.
    df = persistent_engine.create(source=df[df['A'] == 1], name='More Data')
    assert df.shape == (1, 3)
    df = persistent_engine.checkout(name='More Data')
    assert df.shape == (1, 3)
    df = persistent_engine.checkout(name='My Data')
    assert df.shape == (2, 3)
    # Drop the second dataset.
    persistent_engine.drop('More Data')
    df = persistent_engine.checkout(name='My Data')
    assert df.shape == (2, 3)
    with pytest.raises(ValueError):
        persistent_engine.drop('More Data')
    with pytest.raises(ValueError):
        persistent_engine.checkout(name='More Data')
    df = persistent_engine.checkout(name='My Data')
    assert df.shape == (2, 3)


@pytest.mark.parametrize('cached', [True, False])
def test_create_and_commit(cached, persistent_engine, dataset):
    """Test creating and committing datasets via the engine."""
    # Create and checkout a dataset snapshot.
    df = persistent_engine.create(source=dataset, name='My Data')
    assert df.shape == (2, 3)
    df = persistent_engine.commit(df=df[df['A'] == 1], name='My Data')
    assert df.shape == (1, 3)
    df = persistent_engine.checkout(name='My Data')
    assert df.shape == (1, 3)
    df = persistent_engine.checkout(name='My Data', version=0)
    assert df.shape == (2, 3)


def test_dataset_metadata(persistent_engine, dataset):
    """Test accessing snapshot metadata for a dataset via the openclean engine."""
    persistent_engine.create(source=dataset, name='DS')
    persistent_engine.metadata('DS').set_annotation(key='A', value=1)
    persistent_engine.commit(df=dataset, name='DS')
    persistent_engine.metadata('DS').set_annotation(key='A', value=2)
    assert persistent_engine.metadata('DS', version=0).get_annotation(key='A') == 1
    assert persistent_engine.metadata('DS', version=1).get_annotation(key='A') == 2
    with pytest.raises(ValueError):
        persistent_engine.metadata('UNKNOWN')


def test_dataset_snapshots(volatile_engine, dataset):
    """Test accessing snapshots for a dataset via the openclean engine."""
    volatile_engine.load_dataset(source=dataset, name='DS')
    assert len(volatile_engine.history('DS')) == 1
    with pytest.raises(ValueError):
        volatile_engine.history('UNKNOWN')
