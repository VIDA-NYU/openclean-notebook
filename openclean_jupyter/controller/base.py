# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Helper classes for handling requests from components that are rendered in
a notebook environment.
"""

from __future__ import annotations
from typing import Dict, Optional

import pandas as pd

from openclean_jupyter.engine.registry import registry
from openclean_jupyter.engine.command import Transformers


class DatasetLocator(object):
    """The dataset locator is a a pair of dataset name and engine identifier.
    The engine identifier references the OpencleanEngine instance that is
    managing the dataset that is reference by its unique name.
    """
    def __init__(
        self,
        dataset: str,
        engine: str,
        df: Optional[pd.DataFrame] = None
    ):
        """Initialize the dataset locator components.

        Parameters
        ----------
        dataset: string
            Unique dataset name.
        engine: string
            Unique engine instance identifier.
        df: pd.DataFrame
            Optional data frame containing the latest snapshot for the
            referenced dataset.
        """
        self.dataset = dataset
        self.engine = registry.get(engine)
        self._df = df

    @staticmethod
    def deserialize(doc: Dict) -> DatasetLocator:
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
        openclean_jupyter.controller.spreadsheet.DatasetLocator

        Raises
        ------
        ValueError
        """
        if not doc or len(doc) > 2:
            raise ValueError('invalid dataset locator')
        if 'name' not in doc:
            raise ValueError('missing name in dataset locator')
        if 'engine' not in doc:
            raise ValueError('missing engine identifier in dataset locator')
        return DatasetLocator(dataset=doc['name'], engine=doc['engine'])

    def exec(self, cmd: str, args: Dict) -> Transformers:
        """Execute a command on a dataset. The command_id identifies a command
        that is registered with the associated engine. The arguments are a
        command-specific dictionary of key value pairs.

        Returns the locator for the updated dataset snapshot.

        Raises a ValueError if (i) no command identifier is given, (ii) the
        command identifier is unknown, or (iii) the given argument values do
        not satisfy the parameter constraints of the selected command.

        Parameters
        ----------
        cmd: string
            Unique identifier for a command that is registered with the engine.
        args: dict
            Dictionary of command-specific argument values.

        Returns
        -------
        openclean_jupyter.controller.base.DatasetLocator

        Raises
        ------
        ValueError
        """
        # Ensure that a command identifier is given.
        if cmd is None:
            raise ValueError('missing command identifier')
        args = args if args is not None else dict()
        op = self.engine.apply(name=self.dataset)
        self._df = getattr(op, cmd)(args.get('column'))
        return self

    def load(self) -> pd.DataFrame:
        """Load the latest version of the identified dataset.

        Returns
        -------
        pd.DataFrame
        """
        if self._df is None:
            self._df = self.engine.checkout(name=self.dataset)
        return self._df

    def serialize(self) -> Dict:
        """Get dictionary serialization for the dataset locator;

        Returns
        -------
        dict
        """
        return {'name': self.dataset, 'engine': self.engine.identifier}
