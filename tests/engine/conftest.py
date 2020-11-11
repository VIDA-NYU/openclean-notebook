# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the HISTORE-based implementation of the data store."""

import os
import pytest

from histore.archive.manager.persist import PersistentArchiveManager
from histore.archive.manager.mem import VolatileArchiveManager

from openclean_jupyter.engine.base import OpencleanEngine


@pytest.fixture
def persistent_engine(tmpdir):
    """Create a new instance of the Openclean engine with a persistent HISTORE
    data store as the backend.
    """
    return OpencleanEngine(
        identifier='TEST',
        manager=PersistentArchiveManager(basedir=str(tmpdir), create=True),
        basedir=os.path.join(tmpdir, '.annotations')
    )


@pytest.fixture
def volatile_engine():
    """Create a new instance of the Openclean engine with a volatile HISTORE
    data store as the backend.
    """
    return OpencleanEngine(identifier='TEST', manager=VolatileArchiveManager())
