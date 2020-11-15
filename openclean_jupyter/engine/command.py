# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

from __future__ import annotations
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import pandas as pd

from openclean.data.types import Columns
from openclean.operator.transform.update import update
from openclean_jupyter.engine.parameter import Parameter
from openclean_jupyter.datastore.base import Datastore


@dataclass
class FunctionSpec:
    """
    """
    pass


class Namespace(object):
    """
    """
    pass


class FunctionStore(metaclass=ABCMeta):
    """
    """
    @abstractmethod
    def add(self, func: FunctionSpec):
        """
        """
        raise NotImplementedError()

    @abstractmethod
    def namespaces(self) -> List[Namespace]:
        """
        """
        raise NotImplementedError()


class CommandRegistry(object):
    """Registry for commands that can be applied to a single data frame. The
    registry maintains information about available (registered) commands and
    it provides the functionality to add new commands to the registry.
    """
    def __init__(self, store: FunctionStore):
        """Initialize the dictionary that maintains registered commands."""
        # At this point we should 'scan' for implementations of OpencleanCell
        # classes and add them automatically to the registry.
        # For now we simply add a few string functions for demonstration
        # purposes.
        self.store = store
        self.eval('to_lower')(str.lower)
        self.eval('to_upper')(str.upper)
        self.eval('capitalize')(str.capitalize)

    def eval(
        self, name: str, label: Optional[str] = None, help: Optional[str] = None,
        columns: Optional[int] = None, outputs: Optional[int] = None,
        parameters: Optional[List[Parameter]] = None, namespace: Optional[str] = None
    ) -> Callable:
        """Decorator that adds a new function to the registered set of data
        frame transformers.

        Parameters
        ----------
        name: string
            Name of the method that invokes the decorated transformer.
        label: string, default=None
            Optional human-readable name for display purposes.
        help: str, default=None
            Descriptive text for the function. This text can for example be
            displayed as tooltips in a front-end.
        columns: int, default=None
            Specifies the number of input columns that the registered function
            operates on. The function will receive exactly one argument for
            each columns plust arguments for any additional parameters. The
            column values will be the first arguments that are passed to the
            registered function.
        outputs: int, default=None
            Defines the number of scalar output values that the registered
            function returns. By default it is assumed that the function will
            return a single scalar value.
        parameters: list of openclean_jupyter.engine.parameter.Parameter, default=None
            List of declarations for additional input parameters to the
            registered function.
        namespace: string, default=None
            Name of the namespace that this function belongs to. By default all
            functions will be placed in a global namespace.

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
            def update_op(self, columns: Columns):
                """Use the update method of the associated transformer to apply
                the registered function on the latest dataset snapshot. Returns
                the modified data frame.
                """
                return self.update(columns=columns, func=func)
            # Add the created update operator as a class method for the data
            # frame transformer collection.
            setattr(Transformers, name, update_op)
            # Add function together with its metadata to the registry.
            self.store.add(
                FunctionSpec(
                    func=func,
                    namespace=namespace,
                    name=name,
                    label=label,
                    help=help,
                    columns=columns,
                    outputs=outputs,
                    parameters=parameters
                )
            )
            # Return the undecorated function so that it can be used normally.
            return func
        return register_eval

    def serialize(self) -> List[Dict]:
        """Get serialization of registered commands.

        Returns
        -------
        list
        """
        doc = list()
        for ns in self.store.namespaces():
            functions = list()
            for func in ns.functions():
                functions.append(func.to_dict())
            doc.append({'namespace': ns.name, 'functions': functions})
        return doc

    def transformers(self, datastore: Datastore) -> Transformers:
        """Get a object that allows to run registered data frame transformers
        on the given dataset. The dataset is represented by the datastore that
        maintains the dataset history.

        Parameters
        ----------
        datastore: openclean_jupyter.datastore.base.Datastore
            Datastore that manages snapshots for the dataset.

        Returns
        -------
        openclean_jupyter.engine.command.Transformers
        """
        return Transformers(datastore=datastore)


class Transformers(object):
    def __init__(self, datastore: Datastore):
        """Initialize the reference to the datastore that maintains the history
        of the dataset that is being tranformed.

        Parameters
        ----------
        datastore: openclean_jupyter.datastore.base.Datastore
            Datastore for managing dataset snapshots.
        """
        self.datastore = datastore

    def update(self, columns: Columns, func: Callable) -> pd.DataFrame:
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
        df = self.datastore.checkout()
        df = update(df=df, columns=columns, func=func)
        return self.datastore.commit(df=df)
