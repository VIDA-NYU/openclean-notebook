# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Helper classes for accessing datasets as part of requests from components
that are rendered in a notebook environment.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Union

import pandas as pd

from openclean.data.metadata.base import MetadataStore
from openclean.data.types import Scalar
from openclean.engine.library.base import ObjectLibrary
from openclean.engine.library.func import FunctionHandle
from openclean.engine.registry import registry


class Dataset(object):
    """The dataset handle provides access to the current snapshot of the
    dataset that is identified by a given dataset locator.
    """
    def __init__(self, name: str, engine: str):
        """Initialize the dataset locator and the reference to the datastore
        that is responsible for maintaining the dataset.

        Parameters
        ----------
        name: string
            Unique dataset name.
        engine: string
            Identifier of the database engine for the dataset.
        """
        self.name = name
        self.engine = engine
        # Maintain a reference to the dataset handle.
        self._dataset = None

    def checkout(self) -> pd.DataFrame:
        """Load the latest version of the identified dataset.

        Returns
        -------
        pd.DataFrame
        """
        return self.dataset.checkout()

    @property
    def dataset(self):
        """Get reference to the dataset handle.

        Returns
        -------
        """
        if self._dataset is None:
            self._dataset = registry.get(self.engine).dataset(self.name)
        return self._dataset

    @staticmethod
    def deserialize(doc: Dict) -> Dataset:
        """Extract the dataset name and engine identifier from the dataset
        locator in a request body. Expects a dictionary with two elements:
        'name' for the dataset name and 'engine' for the engine identifier.

        The document may be None. Raises a ValueError if an invalid dictionary
        is given.

        Parameters
        ----------
        doc: dict
            Dictionary containing dataset name and engine identifier.

        Returns
        -------
        openclean_jupyter.controller.spreadsheet.base.DatasetLocator

        Raises
        ------
        ValueError
        """
        if not doc or len(doc) > 2:
            raise ValueError('invalid dataset locator')
        if 'name' not in doc:
            raise ValueError('missing name in dataset locator')
        if 'database' not in doc:
            raise ValueError('missing database identifier in dataset locator')
        return Dataset(name=doc['name'], engine=doc['database'])

    def insert(
        self, names: List[str], pos: Optional[int] = None,
        values: Optional[Union[Scalar, FunctionHandle]] = None,
        args: Optional[Dict] = None, sources: Optional[int] = None
    ):
        """Insert one or more columns at a given position into the dataset. One
        column is inserted for each given column name. If the insert position is
        undefined, columns are appended. If the position does not reference
        a valid position (i.e., not between 0 and len(df.columns)) a ValueError
        is raised.

        Values for the inserted columns are generated using a given constant
        value or function. If a function is given, it is expected to return
        exactly one value (e.g., a tuple of len(names)) for each of the inserted
        columns.

        Parameters
        ----------
        names: string, or list(string)
            Names of the inserted columns.
        pos: int, default=None
            Insert position for the new columns. If None, the columns will be
            appended.
        values: scalar or openclean.engine.library.func.FunctionHandle, default=None
            Single value, tuple of values, or library function that is used to
            generate the values for the inserted column(s). If no default is
            specified all columns will contain None.
        args: dict, default=None
            Additional keyword arguments that are passed to the callable together
            with the column values that are extracted from each row.
        sources: int, string, or list(int or string), default=None
            List of source columns from which the input values for the
            callable are extracted.
        """
        self.dataset.insert(
            names=names,
            pos=pos,
            values=values,
            args=args,
            sources=sources
        )

    @property
    def library(self) -> ObjectLibrary:
        """Get reference to object registry for the associated engine.

        Returns
        -------
        openclean.engine.library.base.ObjectLibrary
        """
        return registry.get(self.engine).library

    def serialize(self) -> Dict:
        """Get dictionary serialization for a dataset locator.
        Returns
        -------
        dict
        """
        return {'name': self.name, 'database': self.engine}

    def metadata(self) -> MetadataStore:
        """Get metadata that is associated with the referenced dataset version.

        Returns
        -------
        openclean_jupyter.metadata.metastore.base.MetadataStore

        """
        return self.dataset.datastore.metadata()

    def version(self) -> int:
        """Identifier of the current dataset version.

        Returns
        -------
        int
        """
        return self.dataset.datastore.last_version()
