# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the cached data store."""

import time

from openclean_jupyter.datastore.cache import CachedDatastore


def test_cache_metadata(dataset, store):
    """Test accessing metadata for a dataset in a cached datastore."""
    cached_store = CachedDatastore(datastore=store)
    ds = cached_store.load(source=dataset, name='my_dataset')
    cached_store.metadata(name='my_dataset')\
        .set_annotation(column_id=1, key='type', value='int')
    annos = cached_store.metadata(name='my_dataset', version=ds.version)
    assert annos.get_annotation(column_id=1, key='type') == 'int'


def test_singular_cache(dataset, store):
    """Tast caching datasets with a cache size of one (default)."""
    cached_store = CachedDatastore(datastore=store)
    # -- First dataset --------------------------------------------------------
    df = cached_store.load(source=dataset, name='my_dataset')
    assert df.shape == (2, 3)
    assert len(cached_store._cache) == 1
    assert 'my_dataset' in cached_store._cache
    df = cached_store.checkout('my_dataset')
    assert df.shape == (2, 3)
    df = df[df['A'] == 1]
    df = cached_store.commit(df=df, name='my_dataset')
    assert df.shape == (1, 3)
    assert len(cached_store._cache) == 1
    assert 'my_dataset' in cached_store._cache
    assert len(cached_store.snapshots('my_dataset')) == 2
    # -- Add second dataset ---------------------------------------------------
    df = cached_store.load(source=df, name='next_dataset')
    assert df.shape == (1, 3)
    assert len(cached_store._cache) == 1
    assert 'next_dataset' in cached_store._cache
    df = cached_store.checkout('next_dataset')
    assert df.shape == (1, 3)
    assert len(cached_store.snapshots('next_dataset')) == 1
    # -- Checkout first dataset -----------------------------------------------
    df = cached_store.checkout('my_dataset', version=0)
    assert df.shape == (2, 3)
    assert len(cached_store._cache) == 1
    assert 'my_dataset' in cached_store._cache
    assert not cached_store._cache['my_dataset'].is_last


def test_multi_cache(dataset, store):
    """Test caching datasets in a cache of size two."""
    cached_store = CachedDatastore(datastore=store, cache_size=2)
    cached_store.load(source=dataset, name='first_dataset')
    cached_store.load(source=dataset, name='second_dataset')
    assert len(cached_store._cache) == 2
    assert 'first_dataset' in cached_store._cache
    assert 'second_dataset' in cached_store._cache
    time.sleep(0.1)
    cached_store.commit(df=dataset, name='first_dataset')
    assert len(cached_store._cache) == 2
    assert 'first_dataset' in cached_store._cache
    assert 'second_dataset' in cached_store._cache
    assert cached_store._cache['first_dataset'].ds.version == 1
    time.sleep(0.1)
    cached_store.load(source=dataset, name='third_dataset')
    assert len(cached_store._cache) == 2
    assert 'first_dataset' in cached_store._cache
    assert 'third_dataset' in cached_store._cache
