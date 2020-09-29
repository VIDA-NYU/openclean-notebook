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

import pandas as pd

from datetime import datetime
from typing import Dict, List, Optional, Union

from openclean_jupyter.metadata.profiling.base import Profiler
from openclean_jupyter.metadata.metastore.base import MetadataStore


class DatasetSnapshot(object):
    """Object containing basic information and metadata that is being
    maintained for each version of a dataset in the datastore.
    """
    def __init__(self, version: int, created_at: datetime):
        """Initialize the dataset information.

        Parameters
        ----------
        version: int
            Unique version identifier.
        created_at: datetime.datetime
            Timestamp when the dataset versionwas created.
        """
        self.version = version
        self.created_at = created_at


class Datastore(metaclass=ABCMeta):  # pragma: no cover
    """Interface for the data store that is used to maintain the different
    versions of a dataset that a user creates using the openclean (Jupyter)
    API.

    The data store maintains the history for different datasets that are
    created by the user. Each dataset is identified by a unique name.
    """
    @abstractmethod
    def checkout(
        self, name: str, version: Optional[int] = None
    ) -> pd.DataFrame:
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
        pd.DataFrame

        Raises
        ------
        ValueError
        """
        raise NotImplementedError()

    @abstractmethod
    def commit(
        self, df: pd.DataFrame, name: str, action: Optional[Dict] = None
    ) -> pd.DataFrame:
        """Insert a new version for a dataset. If the dataset name is unknown a
        new dataset archive will be created.

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
        pd.DataFrame
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
    def load(
        self, df: pd.DataFrame, name: str,
        primary_key: Optional[Union[List[str], str]] = None,
        profiler: Optional[Profiler] = None
    ) -> pd.DataFrame:
        """Create an initial dataset archive that is idetified by the given
        name. The given data frame represents the first snapshot in the created
        archive.

        Raises a ValueError if an archive with the given name already exists.

        Parameters
        ----------
        df: pd.DataFrame
            Data frame containing the first versio of the archived dataset.
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
        pd.DataFrame

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
    def snapshots(self, name: str) -> List[DatasetSnapshot]:
        """Get list of handles for all versions of a given dataset. The datset
        is identified by the unique dataset name.

        Raises a ValueError if the dataset name is unknown.

        Parameters
        ----------
        name: string
            Unique dataset name.

        Returns
        -------
        list of openclean_jupyter.datastore.base.DatasetHandle

        Raises
        ------
        ValueError
        """
        raise NotImplementedError()
