# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Interfaces and base classes for the data store that is used to maintain all
versions of a data frame.
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from histore.document.csv.base import CSVFile
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

from openclean_jupyter.metadata.profiling.base import Profiler
from openclean_jupyter.metadata.metastore.base import MetadataStore


"""Type aliases for API methods."""
# Data sources for loading are either pandas data frames or references to files.
Datasource = Tuple[pd.DataFrame, CSVFile, str]


@dataclass
class SnapshotHandle(object):
    """Object containing basic information and metadata that is being
    maintained for each version of a dataset in the datastore.
    """
    # Unique version identifier.
    version: int = None
    # Timestamp when the dataset version was created.
    created_at: datetime = None


@dataclass
class Dataset(SnapshotHandle):
    """The dataset captures the data frame that is associated with a dataset
    snapshot and the version identifier.
    """
    # Data frame containing the data for the dataset snapshot.
    df: pd.DataFrame = None


class Datastore(metaclass=ABCMeta):  # pragma: no cover
    """Interface for the data store that is used to maintain the different
    versions of a dataset that a user creates using the openclean (Jupyter)
    API.

    The data store maintains the history for different datasets that are
    created by the user. Each dataset is identified by a unique name.
    """
    @abstractmethod
    def checkout(self, name: str, version: Optional[int] = None) -> Dataset:
        """Get a specific version of a dataset. The dataset is identified by
        the unique name and the dataset version by the unique version
        identifier.

        Returns the data frame and version number for the dataset snapshot.

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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()
