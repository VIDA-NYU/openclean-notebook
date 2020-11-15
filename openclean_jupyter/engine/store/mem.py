# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Volatile object store implementation that maintains all objects in a
dictionary in main memory.
"""

from openclean_jupyter.engine.store.json import ObjectStore


class VolatileObjectStore(ObjectStore):
    """Object store that maintains all (key, value)-pairs in a dictionary."""
    def __init__(self):
        """Initialize the dictionary that maintains the stored objects."""
        self.db = dict()

    def commit(self):
        """Signal the end of a sequence of operations. Nothing needs to be
        commited here.
        """
        pass

    def delete_object(self, key: str):
        """Delete the object with the given key from the repository. Does not
        raise an error if no object with the given key exists.

        Parameters
        ----------
        key: string
            Unique object identifier.
        """
        if key in self.db:
            del self.db[key]

    def exists_object(self, key: str) -> bool:
        """Check if an object with the given key exists in the object store.

        Parameters
        ----------
        key: string
            Unique object identifier.

        Returns
        -------
        bool
        """
        return key in self.db

    def read_object(self, key: str) -> str:
        """Read the value that is associated with the given key. Returns None if
        no object with the given key exists.

        Parameters
        ----------
        key: string
            Unique object identifier.

        Returns
        -------
        string
        """
        return self.db.get(key)

    def write_object(self, key: str, value: str):
        """Write (key, value)-pair to the store. If an entry with the given key
        exists it is replaced by the given value.
        Parameters
        ----------
        key: string
            Unique object identifier.
        value: string
            Object value.
        """
        self.db[key] = value
