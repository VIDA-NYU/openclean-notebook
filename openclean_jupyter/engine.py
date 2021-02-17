# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""The openclean engine maintains a collection of datasets. Each dataset is
identified by a unique name. Dataset snapshots are maintained by a datastore.
"""

from dataclasses import dataclass
from histore.archive.manager.base import ArchiveManager
from histore.archive.manager.persist import PersistentArchiveManager
from histore.archive.manager.mem import VolatileArchiveManager
from typing import Dict, List, Optional, Tuple

import os

from openclean.engine.base import OpencleanEngine
from openclean.engine.library import ObjectLibrary
from openclean.engine.registry import registry
from openclean.util.core import unique_identifier


@dataclass
class Namespace:
    """Descriptor for namespaces that group functions in the object repository.
    Namespaces are primarily used to group commands for display purposes. The
    namespace class therefore contains a display label (short name) and a
    descriptive help text for the group of commands it represents.
    """
    identifier: str
    label: str
    help: Optional[str] = None
    sort_order: Optional[int] = 0

    def to_dict(self) -> Dict:
        """Get dictionary serialization for the namespace descriptor.

        Returns
        -------
        dict
        """
        return {
            'id': self.identifier,
            'label': self.label,
            'help': self.help,
            'sortOrder': self.sort_order
        }


class OpencleanAPI(OpencleanEngine):
    """The openclean API extends the openclean engine with functionality to display
    user-interface components in a notebook environment.
    """
    def __init__(
        self, identifier: str, manager: ArchiveManager, library: ObjectLibrary,
        namespaces: Optional[List[Namespace]] = list(), basedir: Optional[str] = None,
        cached: Optional[bool] = True
    ):
        """Initialize the engine identifier, the manager for created dataset
        archives, and the library for registered objects.

        Paramaters
        ----------
        identifier: string
            Unique identifier for the engine instance.
        manager: histore.archive.manager.base.ArchiveManager
            Manager for created dataset archives.
        library: openclean.engine.library.base.ObjectLibrary
            Library manager for objects (e.g., registered functions).
        namespaces: list of openclean_jupyter.engine.Namespace, default=list
            List of namespace descriptors.
        basedir: string, default=None
            Path to directory on disk where archive metadata is maintained.
        cached: bool, default=True
            Flag indicating whether the all datastores that are created for
            existing archives are cached datastores or not.
        """
        super(OpencleanAPI, self).__init__(
            identifier=identifier,
            manager=manager,
            library=library,
            basedir=basedir,
            cached=cached
        )
        # Convert the given list of namespaces into a directory.
        self.namespaces = dict()
        for ns in namespaces:
            self.namespaces[ns.identifier] = ns

    def edit(
        self, name: str, n: Optional[int] = None,
        random_state: Optional[Tuple[int, List]] = None
    ):
        """Display the spreadsheet view for a given dataset. The dataset is
        identified by its unique name. Raises a ValueError if no dataset with
        the given name exists.

        Creates a new data frame that contains a random sample of the rows in
        the last snapshot of the identified dataset. This sample is registered
        as a separate dataset with the engine. If neither n nor frac are
        specified a random sample of size 100 is generated.

        Parameters
        ----------
        name: string
            Unique dataset name.
        n: int, default=None
            Number of rows in the sample dataset.
        random_state: int or list, default=None
            Seed for random number generator.

        Raises
        ------
        ValueError
        """
        # Create a sample for the dataset if a sample size was given by the user.
        if n is not None:
            self.sample(name=name, n=n, random_state=random_state)
        # Embed the spreadsheet view into the notebook. Import the spreadsheet
        # embedder here to avoid cyclic dependencies.
        from openclean_jupyter.controller.spreadsheet.base import spreadsheet
        spreadsheet(name=name, engine=self.identifier)

    def library_dict(self) -> Dict:
        """Get serialization of registered library functions and namespaces.

        Returns
        -------
        list
        """
        functions = list()
        for obj in self.library.functions().to_listing():
            cobj = {o: obj[o] for o in obj if o is not 'description'}
            functions.append(cobj)
        return {
            'functions': functions,
            'namespaces': [n.to_dict() for n in self.namespaces.values()]
        }


# -- Engine factory -----------------------------------------------------------

def DB(
    basedir: Optional[str] = None, create: Optional[bool] = False,
    namespaces: Optional[List[Namespace]] = None, cached: Optional[bool] = True
) -> OpencleanAPI:
    """Create an instance of the openclean API for notebook environments.

    Parameters
    ----------
    basedir: string
        Path to directory on disk where archives are maintained.
    create: bool, default=False
        Create a fresh instance of the archive manager if True. This will
        delete all files in the base directory.
    namespaces: list of openclean_jupyter.engine.Namespace, default=None
        List of namespace descriptors.
    cached: bool, default=True
        Flag indicating whether the all datastores that are created for
        existing archives are cached datastores or not.

    Returns
    -------
    openclean_jupyter.engine.OpencleanAPI
    """
    # Create a unique identifier to register the created engine in the
    # global registry dictionary. Use an 8-character key here. Make sure to
    # account for possible conflicts.
    engine_id = unique_identifier(8)
    while engine_id in registry:
        engine_id = unique_identifier(8)
    # Create the engine components and the engine instance itself.
    if basedir is not None:
        histore = PersistentArchiveManager(basedir=basedir, create=create)
        metadir = os.path.join(basedir, '.metadata')
    else:
        histore = VolatileArchiveManager()
        metadir = None
    # Create object library and register three default string functions (for
    # demonstration purposes). At some point, the set of library functions that
    # is registered by default should be read from a configuration file.
    library = ObjectLibrary()
    library.eval(namespace='string')(str.lower)
    library.eval(namespace='string')(str.upper)
    library.eval(namespace='string')(str.capitalize)
    # Add namespace for string functions if not present.
    ns_string = Namespace(
        identifier='string',
        label='Text',
        help='Collection of string operators'
    )
    if namespaces is not None:
        found = False
        for ns in namespaces:
            if ns.identifier == ns_string.identifier:
                found = True
                break
        if not found:
            namespaces.append(ns_string)
    else:
        namespaces = [ns_string]
    # # Create and register the openclean API.
    engine = OpencleanAPI(
        identifier=engine_id,
        manager=histore,
        library=library,
        namespaces=namespaces,
        basedir=metadir,
        cached=cached
    )
    # Register the new engine instance before returning it.
    registry[engine_id] = engine
    return engine
