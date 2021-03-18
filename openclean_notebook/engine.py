# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""The openclean engine maintains a collection of datasets. Each dataset is
identified by a unique name. Dataset snapshots are maintained by a datastore.
"""

from histore.archive.manager.base import ArchiveManager
from histore.archive.manager.persist import PersistentArchiveManager
from histore.archive.manager.mem import VolatileArchiveManager
from typing import Dict, List, Optional, Tuple

import os

from openclean.engine.base import OpencleanEngine
from openclean.engine.library import ObjectLibrary
from openclean.engine.registry import registry
from openclean.util.core import unique_identifier


class OpencleanAPI(OpencleanEngine):
    """The openclean API extends the openclean engine with functionality to display
    user-interface components in a notebook environment.
    """
    def __init__(
        self, identifier: str, manager: ArchiveManager, library: ObjectLibrary,
        basedir: Optional[str] = None, cached: Optional[bool] = True
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
        from openclean_notebook.controller.spreadsheet.base import spreadsheet
        spreadsheet(name=name, engine=self.identifier)

    def library_dict(self) -> Dict:
        """Get serialization of registered library functions and namespaces.

        Returns
        -------
        list
        """
        return {'functions': self.library.functions().to_listing()}


# -- Engine factory -----------------------------------------------------------

def DB(
    basedir: Optional[str] = None, create: Optional[bool] = False,
    cached: Optional[bool] = True
) -> OpencleanAPI:
    """Create an instance of the openclean API for notebook environments.

    Parameters
    ----------
    basedir: string
        Path to directory on disk where archives are maintained.
    create: bool, default=False
        Create a fresh instance of the archive manager if True. This will
        delete all files in the base directory.
    cached: bool, default=True
        Flag indicating whether the all datastores that are created for
        existing archives are cached datastores or not.

    Returns
    -------
    openclean_notebook.engine.OpencleanAPI
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
    # # Create and register the openclean API.
    engine = OpencleanAPI(
        identifier=engine_id,
        manager=histore,
        library=library,
        basedir=metadir,
        cached=cached
    )
    # Register the new engine instance before returning it.
    registry[engine_id] = engine
    return engine
