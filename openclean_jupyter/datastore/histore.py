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

from typing import Dict, List, Optional

import os
import pandas as pd

from histore.archive.base import Archive

from openclean_jupyter.datastore.base import Datastore, SnapshotHandle
from openclean_jupyter.metadata.metastore.fs import FileSystemMetadataStore


ANNOTATION_FOLER = '.annotations'


class HISTOREDatastore(Datastore):
    """Data store implementation that is based on HISTORE. This class is a
    simple wrapper around a HISTORE archive.
    """
    def __init__(self, basedir: str, archive: Archive):
        """Initialize the base directory for archive metadata and the reference
        to the archive.

        Parameters
        ----------
        basedir: string
            Base directory for storing archive metadata.
        archive: histore.archive.base.Archive
            Archive for dataset snapshots.
        """
        self.basedir = basedir
        self.archive = archive
        # Maintain a reference to the snapshot for the last version
        self._last_snapshot = archive.snapshots().last_snapshot()

    def checkout(self, version: Optional[int] = None) -> pd.DataFrame:
        """Get a specific dataset snapshot. The snapshot is identified by
        the unique version identifier.

        Raises a ValueError if the given version is unknown.

        Parameters
        ----------
        version: int
            Unique dataset version identifier.

        Returns
        -------
        pd.DataFrame

        Raises
        ------
        ValueError
        """
        return self.archive.checkout(version=version)

    def commit(self, df: pd.DataFrame, action: Optional[Dict] = None) -> pd.DataFrame:
        """Insert a new version for a dataset. Returns the inserted data frame
        (after potentially modifying the row indexes).

        Parameters
        ----------
        df: pd.DataFrame
            Data frame containing the new dataset version that is being stored.
        action: dict, default=None
            Optional description of the action that created the new dataset
            version.

        Returns
        -------
        pd.DataFrame
        """
        self._last_snapshot = self.archive.commit(doc=df)
        return self.archive.checkout(version=self._last_snapshot.version)

    def last_version(self) -> int:
        """Get a identifier for the last version of a dataset.

        Returns
        -------
        int
        """
        return self._last_snapshot.version

    def metadata(self, version: Optional[int] = None) -> FileSystemMetadataStore:
        """Get metadata that is associated with the referenced dataset version.
        If no version is specified the metadata collection for the latest
        version is returned.

        Raises a ValueError if the dataset version is unknown.

        Parameters
        ----------
        version: int
            Unique dataset version identifier.

        Returns
        -------
        openclean_jupyter.metadata.metastore.base.MetadataStore

        Raises
        ------
        ValueError
        """
        if version is None:
            version = self.last_version()
        metadir = os.path.join(
            self.basedir,
            ANNOTATION_FOLER,
            str(version)
        )
        return FileSystemMetadataStore(basedir=metadir)

    def snapshots(self) -> List[SnapshotHandle]:
        """Get list of handles for all versions of a given dataset.

        Returns
        -------
        list of openclean_jupyter.datastore.base.SnapshotHandle
        """
        result = list()
        for snapshot in self.archive.snapshots():
            result.append(
                SnapshotHandle(
                    version=snapshot.version,
                    created_at=snapshot.transaction_time
                )
            )
        return result
