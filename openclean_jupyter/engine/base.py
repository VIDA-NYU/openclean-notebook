# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

import pandas as pd

from typing import Dict, List, Optional, Union

from openclean_jupyter.controller.spreadsheet import spreadsheet
from openclean_jupyter.datastore.base import Datastore, SnapshotHandle
from openclean_jupyter.engine.command import CommandRegistry
from openclean_jupyter.metadata.metastore.base import MetadataStore


class OpencleanEngine(object):
    """The idea of the engine is to wrap a datastore and provide additional
    functionality to show a spreadsheet view, register new commands, etc. Many
    of the methods for this class are direct copies of the methods that are
    implemented by the data store.
    """
    def __init__(self, identifier: str, datastore: Datastore):
        """Initialize the identifier and the reference to the underlying data
        store. Each engine has a unique identifier that is used by the API
        handlers to access the engine instance.

        Paramaters
        ----------
        identifier: string
            Unique identifier for the engine instance.
        datastore: openclean_jupyter.datastore.base.Datastore
            Datastore for managing dataset snapshots.
        """
        self.identifier = identifier
        self.datastore = datastore
        self.register = CommandRegistry()

    def apply(self, name: str) -> CommandRegistry:
        """Get object that allows to run registered (column) commands on the
        current version of a dataset that is identified by its unique name.

        Parameters
        ----------
        name: string
            Unique dataset name.

        Returns
        -------
        openclean_jupyter.engine.command.CommandRegistry
        """
        return self.register.transformers(datastore=self.datastore, name=name)

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
        return self.datastore.checkout(name=name, version=version)

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
        df, _ = self.datastore.commit(df=df, name=name)
        return df

    def drop_dataset(self, name: str):
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
        self.datastore.drop(name=name)

    def edit(self, name: str):
        """Display the spreadsheet view for a given dataset. The dataset is
        identified by its unique name. Raises a ValueError if no dataset with
        the given name exists.

        Parameters
        ----------
        name: string
            Unique dataset name.

        Raises
        ------
        ValueError
        """
        # Get the descriptor for the last snapshot in the dataset history. This
        # will raise an error if the dataset is unknown. The list of snapshots
        # cannot be empty so it is safe to access the last entry immediately.
        self.history(name=name)
        # Embed the spreadsheet view into the notebook.
        spreadsheet(name=name, engine=self.identifier)

    def history(self, name: str) -> List[SnapshotHandle]:
        """Get list of snapshot handles for all versions of a given dataset.
        The datset is identified by the unique dataset name.

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

    def load_dataset(
        self, df: pd.DataFrame, name: str,
        primary_key: Optional[Union[List[str], str]] = None,
        profiler: str = None
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
            profiler: string, default=None
            Optional identifier for the profiler that is used for the dataset.
        primary_key: string or list, default=None
            Column(s) that are used to generate identifier for rows in the
            archive.

        Returns
        -------
        pd.DataFrame

        Raises
        ------
        ValueError
        """
        return self.datastore.load(df=df, name=name)

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
