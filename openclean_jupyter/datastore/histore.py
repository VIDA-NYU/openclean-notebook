# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Implementation of the data store that is based on HISTORE. For each dataset
a new HISTORE archive will be maintained. This archive is augmented with
storage of dataset metadata.
"""

import os
import pandas as pd

from typing import Dict, List, Optional, Union

from histore.archive.base import Archive
from histore.archive.manager.base import ArchiveManager

from openclean_jupyter.datastore.base import Datastore, DatasetSnapshot
from openclean_jupyter.metadata.profiling.base import Profiler
from openclean_jupyter.metadata.metastore.fs import FileSystemMetadataStore


ANNOTATION_FOLER = '.annotations'


class HISTOREDatastore(Datastore):
    """Data store implementation that is based on HISTORE. This class is a
    simple wrapper around a HISTORE archive manager.
    """
    def __init__(self, basedir: str, histore: ArchiveManager):
        """Initialize the base directory for archive metadata and the reference
        to the archive manager.

        Parameters
        ----------
        basedir: string
            Base directory for storing archive metadata.
        histore: histore.archive.manager.base.ArchiveManager
            HISTORE archive manager instance that is used to maintain all
            dataset snapshots.
        """
        self.basedir = basedir
        self.histore = histore

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
        return self._get_archive(name=name).checkout(version=version)

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
        archive = self._get_archive(name=name)
        snapshot = archive.commit(doc=df)
        return archive.checkout(version=snapshot.version)

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
        self.histore.delete(self._get_archive_id(name=name))

    def _get_archive(self, name: str) -> Archive:
        """Get handle for the archive with the given name. Raises a
        ValueError if no archive with the given name exists.

        Parameters
        ----------
        name: string
            Unique archive name.

        Returns
        -------
        histore.archive.base.Archive

        Raises
        ------
        ValueError
        """
        return self.histore.get(self._get_archive_id(name=name))

    def _get_archive_id(self, name: str) -> str:
        """Get identifier for the archive with the given name. Raises a
        ValueError if no archive with the given name exists.

        Parameters
        ----------
        name: string
            Unique archive name.

        Returns
        -------
        string

        Raises
        ------
        ValueError
        """
        descriptor = self.histore.get_by_name(name=name)
        if descriptor is not None:
            return descriptor.identifier()
        raise ValueError("unknown archive {}".format(name))

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
        descriptor = self.histore.create(name=name, primary_key=primary_key)
        archive = self.histore.get(descriptor.identifier())
        snapshot = archive.commit(doc=df)
        if profiler is not None:
            doc = profiler.profile(df)
            self.metadata(name=name, version=snapshot.version)\
                .set_annotation('profiler', doc)
        return self.checkout(name=name, version=snapshot.version)

    def metadata(
        self, name: str, version: Optional[int] = None
    ) -> FileSystemMetadataStore:
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
        archive_id = self._get_archive_id(name=name)
        if version is None:
            version = self.histore\
                .get(archive_id)\
                .snapshots()\
                .last_snapshot()\
                .version
        metadir = os.path.join(
            self.basedir,
            ANNOTATION_FOLER,
            archive_id,
            str(version)
        )
        return FileSystemMetadataStore(basedir=metadir)

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
        result = list()
        for s in self._get_archive(name=name).snapshots():
            ds = DatasetSnapshot(
                version=s.version,
                created_at=s.transaction_time
            )
            result.append(ds)
        return result
