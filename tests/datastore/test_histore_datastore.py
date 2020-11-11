# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the HISTORE-based implementation of the data store."""

import pytest

from openclean.operator.transform.update import update


def test_create_dataset(store, dataset):
    """Test creating a dataset from a given data frame."""
    df_1 = store.load(source=dataset, name='my_dataset')
    assert df_1.shape == (2, 3)
    df_1 = store.checkout('my_dataset')
    assert df_1.shape == (2, 3)
    # Error when loading (creating) new dataset with existing name.
    with pytest.raises(ValueError):
        store.load(source=dataset, name='my_dataset')
    df_2 = store.load(source=dataset, name='my_second_dataset')
    assert df_2.shape == (2, 3)
    # Delete first dataset.
    store.drop('my_dataset')
    # Error when accessing the dataset ans when attempting to delete it again.
    with pytest.raises(ValueError):
        store.checkout('my_dataset')
    with pytest.raises(ValueError):
        store.drop('my_dataset')
    # The second dataset is still accessible.
    df_2 = store.checkout('my_second_dataset')
    assert df_2.shape == (2, 3)


def test_dataset_history(store, dataset):
    """Test updates to a given dataset and retrieving all dataset versions."""
    df = store.load(source=dataset, name='my_dataset')
    df = store.commit(df=update(df=df, columns='B', func=1), name='my_dataset')
    df = store.commit(df=update(df=df, columns='C', func=2), name='my_dataset')
    snapshots = store.snapshots('my_dataset')
    assert len(snapshots) == 3
    # Version 1
    df = store.checkout('my_dataset', version=snapshots[0].version)
    assert list(df['A']) == [1, 3]
    assert list(df['B']) == [2, 4]
    assert list(df['C']) == [3, 5]
    # Version 2
    df = store.checkout('my_dataset', version=snapshots[1].version)
    assert list(df['A']) == [1, 3]
    assert list(df['B']) == [1, 1]
    assert list(df['C']) == [3, 5]
    # Version 3
    df = store.checkout('my_dataset', version=snapshots[2].version)
    assert list(df['A']) == [1, 3]
    assert list(df['B']) == [1, 1]
    assert list(df['C']) == [2, 2]


def test_dataset_metadata(store, dataset):
    """Test updating and retrieving metadata objects for different dataset
    versions.
    """
    # Create two snapshots for a dataset and annotate one column for each with
    # a different data type string.
    df = store.load(source=dataset, name='my_dataset')
    store.metadata(name='my_dataset')\
        .set_annotation(column_id=1, key='type', value='int')
    df = store\
        .commit(df=update(df=df, columns='B', func=1), name='my_dataset')
    store.metadata(name='my_dataset')\
        .set_annotation(column_id=1, key='type', value='str')
    # Assert that the different snapshots have different type annotations for
    # column 1.
    snapshots = store.snapshots('my_dataset')
    annos = store.metadata(name='my_dataset', version=snapshots[0].version)
    assert annos.get_annotation(column_id=1, key='type') == 'int'
    annos = store.metadata(name='my_dataset')
    assert annos.get_annotation(column_id=1, key='type') == 'str'


def test_last_dataset_version(store, dataset):
    """Test getting the version identifier for the last snapshot of a dataset."""
    ds = store.load(source=dataset, name='my_dataset')
    assert store.last_version('my_dataset') == ds.version
    ds = store.checkout('my_dataset')
    assert store.last_version('my_dataset') == ds.version
    with pytest.raises(ValueError):
        store.last_version('unknown_dataset')
