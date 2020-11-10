# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Implementation of the datastore class that caches dataset snapshots in
memory.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

from openclean_jupyter.datastore.base import Dataset, Datastore, Datasource, SnapshotHandle
from openclean_jupyter.metadata.metastore.base import MetadataStore
from openclean_jupyter.metadata.profiling.base import Profiler


@dataclass
class CacheEntry:
    """Entry in a datastore cache. Maintains the dataset handle and a flag that
    indicates whether this dataset represents the last snapshot in the dataset
    history. This flag is used to determine whether a dataset version matches
    a requested dataset where the version identifier is None.
    """
    ds: Dataset = None
    created_at: datetime = None
    is_last: bool = None

    def matches_version(self, version: Optional[int] = None) -> bool:
        """Return True if the cached snapshot matches the given dataset version.

        Parameters
        ----------
        version: int, default=None
            Unique dataset snapshot identifier.

        Returns
        -------
        bool
        """
        if version is None and self.is_last:
            return True
        if version == self.ds.version:
            return True
        return False


class CachedDatastore(Datastore):
    """Wrapper around a datastore that maintains certain dataset versions in a
    main memory cache. The main idea is to keep the last commited or checked out
    version of each dataset in memory (with a total limit in the number of cached
    datasets). This follows the assumption that the spreadsheet view will always
    display (and modify) this version (and only this version).
    """
    def __init__(self, datastore: Datastore, cache_size: Optional[int] = 1):
        """Initialize the reference to the wrapped datastore and the size of
        the cache (i.e., number of archives for which a dataset is maintained
        in cache).

        Parameters
        ----------
        datastore: openclean_jupyter.datastore.base.Datastore
            Reference to the datastore that persists the datasets.
        cache_size: int, default=1
            Max. number of archives for which a dataset is maintained in cache.
            In most cases we envision that the spreadsheet view operates on a
            single dataset. This is why the default is set to one.
        """
        self.datastore = datastore
        self.cache_size = cache_size
        # The cache maintains a mapping from dataaset names to tuples of
        # (dataset, version number)-pairs. We maintain at most one entry
        # per dataset in cache. The assumption is that this entry is accessed
        # and replaced frequently (e.g., by the spreadsheet view). Thus, a
        # dictionary should provide the best performance. For least recently
        # used cache eviction we have to accept the cost of iterating over the
        # whole dictionary (this operation should occur infrequent).
        self._cache = dict()

    def checkout(self, name: str, version: Optional[int] = None) -> Dataset:
        """Get a specific version of a dataset. The dataset is identified by
        the unique name and the dataset version by the unique version
        identifier.

        Raises a ValueError if the dataset or the given version are unknown.

        Parameters
        ----------
        name: string
            Unique dataset name.
        version: int
            Unique dataset version identifier.

        Returns
        -------
        openclean_jupyter.datastore.base.Dataset

        Raises
        ------
        ValueError
        """
        # Serve dataset from cache if present.
        if name in self._cache:
            entry = self._cache[name]
            # Ensure that the cached version matches the requested version.
            if entry.matches_version(version=version):
                return entry.ds
        # Dataset has not been found in the cache. Checkout the dataset from
        # the datastore and add it to the cache.
        ds = self.datastore.checkout(name=name, version=version)
        is_last = version is None or version == self.last_version(name=name)
        self._update_cache(name=name, dataset=ds, is_last=is_last)
        return ds

    def commit(
        self, df: pd.DataFrame, name: str, action: Optional[Dict] = None
    ) -> Dataset:
        """Insert a new version for a dataset. If the dataset name is unknown a
        new dataset archive will be created.

        Returns the inserted data frame (after potentially modifying the row
        indexes) and the version identifier for the commited version.

        Parameters
        ----------
        df: pd.DataFrame
            Data frame containing the new dataset version that is being stored.
        name: string
            Unique dataset name.
        action: dict, default=None
            Optional description of the action that created the new dataset
            version.

        Returns
        -------
        openclean_jupyter.datastore.base.Dataset
        """
        ds = self.datastore.commit(df=df, name=name, action=action)
        self._update_cache(name=name, dataset=ds)
        return ds

    def drop(self, name: str):
        """Delete the full history for the dataset with the given name. Raises
        a ValueError if the dataset name is unknonw.

        Parameters
        ----------
        name: string
            Unique dataset name.

        Raises
        ------
        ValueError
        """
        # Evict cached dataset from cache.
        if name in self._cache:
            del self._cache[name]
        self.datastore.drop(name=name)

    def last_version(self, name: str) -> int:
        """Get a identifier for the last version of a dataset.

        Raises a ValueError if the dataset or the given version are unknown.

        Parameters
        ----------
        name: string
            Unique dataset name.

        Returns
        -------
        int

        Raises
        ------
        ValueError
        """
        return self.datastore.last_version(name=name)

    def load(
        self, source: Datasource, name: str,
        primary_key: Optional[Union[List[str], str]] = None,
        profiler: Optional[Profiler] = None
    ) -> Dataset:
        """Create an initial dataset archive that is idetified by the given
        name. The given data frame represents the first snapshot in the created
        archive.

        Raises a ValueError if an archive with the given name already exists.

        Parameters
        ----------
        source: pd.DataFrame or string
            Data frame or file containing the first version of the archived
            dataset.
        name: string
            Unique dataset name.
        primary_key: string or list, default=None
            Column(s) that are used to generate identifier for rows in the
            archive.
        profiler: openclean_jupyter.metadata.profiling.base.Profiler,
                default=None
            Optional profiler that is used for the dataset versions that are
            added to the archive.

        Returns
        -------
        openclean_jupyter.datastore.base.Dataset

        Raises
        ------
        ValueError
        """
        ds = self.datastore.load(
            source=source,
            name=name,
            primary_key=primary_key,
            profiler=profiler
        )
        self._update_cache(name=name, dataset=ds)
        return ds

    def metadata(
        self, name: str, version: Optional[int] = None
    ) -> MetadataStore:
        """Get metadata that is associated with the referenced dataset version.
        If no version is specified the metadata collection for the latest
        version is returned.

        Raises a ValueError if the dataset or the specified version is unknown.

        Parameters
        ----------
        name: string
            Unique dataset name.
        version: int
            Unique dataset version identifier.

        Returns
        -------
        openclean_jupyter.metadata.metastore.base.MetadataStore

        Raises
        ------
        ValueError
        """
        return self.datastore.metadata(name=name, version=version)

    def snapshots(self, name: str) -> List[SnapshotHandle]:
        """Get list of handles for all versions of a given dataset. The datset
        is identified by the unique dataset name.

        Raises a ValueError if the dataset name is unknown.

        Parameters
        ----------
        name: string
            Unique dataset name.

        Returns
        -------
        list of openclean_jupyter.datastore.base.SnapshotHandle

        Raises
        ------
        ValueError
        """
        return self.datastore.snapshots(name=name)

    def _update_cache(self, name: str, dataset: Dataset, is_last: Optional[bool] = True):
        """Update the cache entry for the given dataset. If an entry for a dataset
        with the given name exists in the cache, the existing entry will be replaced.
        In case of a cache miss an new entry is added to the cache (if the maximum)
        size is not reached. In case that the cache is full, the least recently
        added entry will be removed.

        Parameters
        ----------
        name: string
            Unique dataset name.
        dataset: openclean_jupyter.datastore.base.Dataset
            Dataset snapshot handle.
        is_last: bool, default=True
            Flag indicating whether the snapshot is the last in the history of
            the dataset.
        """
        if name not in self._cache and len(self._cache) == self.cache_size:
            # Find least recently added entry in the cache for eviction.
            first_ts = None
            evict_name = None
            for key, item in self._cache.items():
                if first_ts is None or item.created_at < first_ts:
                    first_ts = item.created_at
                    evict_name = key
            del self._cache[evict_name]
        entry = CacheEntry(ds=dataset, is_last=is_last, created_at=datetime.now())
        self._cache[name] = entry
