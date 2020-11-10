# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the HISTORE-based implementation of the data store."""

import pandas as pd
import pytest

from histore import PersistentArchiveManager
from openclean_jupyter.datastore.histore import HISTOREDatastore
from openclean_jupyter.engine.base import OpencleanEngine


@pytest.fixture
def dataset():
    """Returns a basif data frame with three columns and two rows."""
    return pd.DataFrame(data=[[1, 2, 3], [3, 4, 5]], columns=['A', 'B', 'C'])


@pytest.fixture
def engine(tmpdir):
    """Create a new instance of the Openclean engine with a HISTORE data
    store as the backend.
    """
    store = HISTOREDatastore(
        basedir=str(tmpdir),
        histore=PersistentArchiveManager(basedir=str(tmpdir))
    )
    return OpencleanEngine(identifier='TEST', datastore=store)


def test_dataset_update(engine, dataset):
    """Test updates to a given dataset and retrieving all dataset versions."""
    engine.load_dataset(source=dataset, name='my_dataset', primary_key='A')
    engine.apply('my_dataset').update('B', 1)
    engine.apply('my_dataset').update('C', 2)
    # Get version history.
    snapshots = engine.history('my_dataset')
    assert len(snapshots) == 3
    # Version 1
    df = engine.checkout('my_dataset', version=snapshots[0].version).df
    assert list(df['A']) == [1, 3]
    assert list(df['B']) == [2, 4]
    assert list(df['C']) == [3, 5]
    # Version 2
    df = engine.checkout('my_dataset', version=snapshots[1].version).df
    assert list(df['A']) == [1, 3]
    assert list(df['B']) == [1, 1]
    assert list(df['C']) == [3, 5]
    # Version 3
    df = engine.checkout('my_dataset', version=snapshots[2].version).df
    assert list(df['A']) == [1, 3]
    assert list(df['B']) == [1, 1]
    assert list(df['C']) == [2, 2]
