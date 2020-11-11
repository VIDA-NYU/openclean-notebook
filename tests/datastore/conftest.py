# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Fixtures for datastore unit tests."""

import pytest

from histore import PersistentArchiveManager
from openclean_jupyter.datastore.histore import HISTOREDatastore


@pytest.fixture
def store(tmpdir):
    """Create a new instance of the HISTORE data store."""
    manager = PersistentArchiveManager(basedir=str(tmpdir))
    archive = manager.get(manager.create('test').identifier())
    return HISTOREDatastore(archive=archive)
