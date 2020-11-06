# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.


import uuid

from typing import Optional

from histore import PersistentArchiveManager
from openclean_jupyter.datastore.cache import CachedDatastore
from openclean_jupyter.datastore.histore import HISTOREDatastore
from openclean_jupyter.engine.base import OpencleanEngine
from openclean_jupyter.engine.registry import registry


def DB(
    basedir: Optional[str], create: Optional[bool] = False,
    cache_size: Optional[int] = 1
) -> OpencleanEngine:
    """Create an instance of the openclean-goes-jupyter engine. This test
    implementation uses HISTORE as the underlying datastore. All files will
    be stored in the given base directory. If no base directory is given the
    HISTORE default will be used (i.e., either the directory that is specified
    in the environment variable HISTORE_BASEDIR or the .histore folder in the
    user's home directory).

    If the create flag is True all existing files in the base directory will be
    removed.

    Parameters
    ----------
    basedir: string
        Path to dorectory on disk where archives are maintained.
    create: bool, default=False
        Create a fresh instance of the archive manager if True. This will
        delete all files in the base directory.
    cache_size: int, default=1
        Max. number of archives for which a dataset is maintained in cache.
        By default, a cache of size one is used. If the cache_size is None
        no caching will occur.

    Returns
    -------
    openclean_jupyter.engine.base.OpencleanEngine
    """
    # Create a unique identifier to register the created engine in the
    # global registry dictionary. Use an 8-character key here. Make sure to
    # account for possible conflicts.
    engine_id = str(uuid.uuid4()).replace('-', '')[:8]
    while engine_id in registry:
        engine_id = str(uuid.uuid4()).replace('-', '')[:8]
    # Create the engine components and the engine instance itself.
    histore = PersistentArchiveManager(basedir=basedir, create=create)
    datastore = HISTOREDatastore(basedir=histore.basedir, histore=histore)
    if cache_size > 0:
        datastore = CachedDatastore(datastore=datastore, cache_size=cache_size)
    engine = OpencleanEngine(identifier=engine_id, datastore=datastore)
    # Register the new engine instance before returning it.
    registry[engine_id] = engine
    return engine
