# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

from __future__ import annotations
from typing import Callable, List, Union

import pandas as pd

from openclean.operator.transform.update import update
from openclean_jupyter.datastore.base import Datastore


class CommandRegistry(object):
    """Registry for commands that can be applied to a single data frame. The
    registry maintains information about available (registered) commands and
    it provides the functionality to add new commands to the registry.
    """
    def __init__(self):
        """Initialize the dictionary that maintains registered commands."""
        self._registry = dict()
        # At this point we should 'scan' for implementations of OpencleanCell
        # classes and add them automatically to the registry.
        # For now we simply add a few string functions for demonstration
        # purposes.
        self.eval('to_lower')(str.lower)
        self.eval('to_upper')(str.upper)
        self.eval('capitalize')(str.capitalize)

    def eval(self, name: str) -> Callable:
        """Decorator that adds a new function to the registered set of data
        frame transformers.

        Parameters
        ----------
        name: string
            Name of the method that invokes the decorated transformer.

        Returns
        -------
        callable
        """
        def register_eval(func: Callable) -> Callable:
            """Decorator that creates a data frame transformer that uses the
            given function to update values in one or more columns of a data
            frame. The given function is wrapped inside an evaluation function
            that will be evaluated on individual rows of a data frame.

            This function will be added to the class definition of the data
            frame transformer collection.
            """
            def update_op(self, columns):
                """The update operator checks out the latest version of the
                dataset that is associated with a transformer instance. It
                the evaluates the function on each data frame row to create
                an updated snapshot that is then committed to the datastore.
                """
                df = self.datastore.checkout(name=self.name)
                df = update(df=df, columns=columns, func=func)
                return self.datastore.commit(df=df, name=self.name)
            # Add the created update operator as a class method for the data
            # frame transformer collection.
            setattr(Transformers, name, update_op)
            # Add function metadata to the registry. In future versions we want
            # to maintain function parameter definitions here.
            self._registry[name] = func
            # Return the undecorated function so that it can be used normally.
            return func
        return register_eval

    def serialize(self) -> List:
        """Get serialization of registered commands.

        Returns
        -------
        list
        """
        return sorted(list(self._registry.keys()))

    def transformers(self, datastore: Datastore, name: str) -> Transformers:
        """Get a object that allows to run registered data frame transformers
        on the given data frame version.

        Parameters
        ----------
        datastore: openclean_jupyter.datastore.base.Datastore
            Datastore that manages snapshots for the dataset.
        name: string
            Unique dataset name.

        Returns
        -------
        openclean_jupyter.engine.command.Transformers
        """
        return Transformers(datastore=datastore, name=name)


class Transformers(object):
    def __init__(self, datastore: Datastore, name: str):
        """Initialize the reference to the dataset and the datastore that is
        used to checkout and commit the updated dataset versions.

        Parameters
        ----------
        datastore: openclean_jupyter.datastore.base.Datastore
            Datastore for managing dataset snapshots.
        name: string
            Unique name of the dataset that is being updated.
        """
        self.datastore = datastore
        self.name = name

    def update(
        self, columns: Union[int, str, List[Union[int, str]]], func: Callable
    ) -> pd.DataFrame:
        """Update a given column (or list of columns) by applying the given
        function.

        Parameters
        ----------
        columns: int, string, or list(int or string)
            Single column or list of column index positions or column names.
        func: callable or openclean.function.eval.base.EvalFunction
            Callable that accepts a data frame row as the only argument and
            outputs a (modified) list of value(s).

        Returns
        -------
        pd.DataFrame
        """
        df = self.datastore.checkout(name=self.name)
        df = update(df=df, columns=columns, func=func)
        return self.datastore.commit(df=df, name=self.name)
