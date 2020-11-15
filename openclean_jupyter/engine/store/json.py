# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Implementation of the object repository using an object store that maintains
all objects as Json serializations serializations in an (key, value)-store.
"""

from __future__ import annotations
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Set, Type

import json

from histore.archive.store.fs.reader import default_decoder
from histore.archive.store.fs.writer import DefaultEncoder

from openclean.util.core import unique_identifier
from openclean_jupyter.engine.store.base import ObjectHandle, ObjectRepository


"""Metadata file name."""
METADATA_FILE = '.registry'


class ObjectStore(metaclass=ABCMeta):  # pargma: no cover
    """Abstract class for a simple object store that maintains serialized objects
    as (key, value)-pairs. Provides methods to access and manipulate objects in
    the store.

    Defines a `commit()` method to signal the end of operation sequences, i.e.,
    during delete and insert we delete/write the (key, value)-pair for and
    object and then for the metadata index. Commit is called after the second
    operation in case the store implementation needs to push changes to a remote
    repository (e.g., for store implementation that keeps all data in a git
    repository).
    """
    @abstractmethod
    def commit(self):
        """Signal the end of a sequence of operations. Commit is called by the
        default object repository at the end of insert and delete operations.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_object(self, key: str):
        """Delete the object with the given key from the repository. Does not
        raise an error if no object with the given key exists.

        Parameters
        ----------
        key: string
            Unique object identifier.
        """
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()


class RepoObjectHandle(ObjectHandle):
    """Handle for objects that are stored in the default repository. The handle
    maintains the name, namespace, data type, and the unique object identifier.
    Each repository handle also maintains a reference to the object store to
    allow loading the stored object.
    """
    def __init__(
        self, identifier: str, dtype: str, name: str, store: ObjectStore,
        decoder: Callable, namespace: Optional[str] = None
    ):
        """Initialize the object properties.

        Parameters
        ----------
        identifier: string
            Unique object identifier.
        dtype: string
            Object data type identifier.
        name: string
            Unique object name.
        store: openclean_jupyter.engine.store.base.ObjectStore
            Object store that maintains object serializations.
        decoder: callable
            Json decoder.
        namespace: string, default=None
            Optional namespace identifier for the object.
        """
        super(RepoObjectHandle, self).__init__(
            dtype=dtype,
            name=name,
            namespace=namespace
        )
        self.identifier = identifier
        self.store = store
        self.decoder = decoder

    @staticmethod
    def from_dict(doc: Dict, store: ObjectStore, decoder: Callable) -> RepoObjectHandle:
        """Create an object descriptor instance from a dictionary serialization.

        Parameters
        ----------
        doc: dict
            Object descriptor serialization as created by the `to_dict()` method.
        store: openclean_jupyter.engine.store.base.ObjectStore
            Object store that maintains object serializations.
        decoder: callable
            Json decoder.

        Returns
        -------
        openclean_jupyter.engine.store.index.RepoObjectHandle
        """
        return RepoObjectHandle(
            identifier=doc['id'],
            name=doc['name'],
            namespace=doc['namespace'],
            dtype=doc['dtype'],
            store=store,
            decoder=decoder
        )

    def get_object(self) -> Dict:
        """Get the dictionary serialization for the object from the object
        store.

        Returns
        -------
        dict
        """
        return json.loads(self.store.read_object(self.identifier), object_hook=self.decoder)

    def to_dict(self) -> Dict:
        """Create a dictionary serialization for this descriptor.

        Returns
        -------
        dict
        """
        return {
            'id': self.identifier,
            'name': self.name,
            'namespace': self.namespace,
            'dtype': self.dtype
        }


class DefaultObjectRepository(ObjectRepository):
    """Default implementation of the object repository API that maintains all
    objects in a given object store. Each object is assigned a unique identifier
    and serialized as a Json dictionary. Serialized objects are stored with their
    unique identifier as key in a (key, value)-store. The implementation provides
    flexibility in the object store that is used (e.g., file system, S3 buckets,
    GitHub, ...).

    Maintains the list of object descriptors in a memory cache. This implementation
    is therefore not suitable for concurrent access where multiple user concurrently
    access and modify data that is stored remote.
    """
    def __init__(
        self, store: ObjectStore, encoder: Optional[Type] = None,
        decoder: Optional[Callable] = None
    ):
        """Initialize the object store and the Json encoder and decoder. If the
        metadata file exists it is read into the memory cache.

        Parameters
        ----------
        store: openclean_jupyter.engine.store.base.ObjectStore
            Implementation of the object store that maintains object serializations
            as (key, value)-pairs.
        encoder
        decoder
        """
        # Set the base directory and ensure that the directory exists.
        self.store = store
        self.encoder = encoder if encoder is not None else DefaultEncoder
        self.decoder = decoder if decoder is not None else default_decoder
        # Initialize the memory cache of object metadata. Read the metadata
        # from the registry file if it exists.
        self._metadata = defaultdict(dict)
        if self.store.exists_object(METADATA_FILE):
            for doc in json.loads(self.store.read_object(METADATA_FILE)):
                obj = RepoObjectHandle.from_dict(
                    doc,
                    store=self.store,
                    decorator=self.decorator
                )
                self._metadata[obj.namespace][obj.name] = obj

    def find_objects(
        self, dtype: Optional[str] = None, namespace: Optional[str] = None
    ) -> List[ObjectHandle]:
        """Get list of objects in the object store. The result can be filtered
        based on the data type and/or namespace. If both query parameters are
        None the full list of objects will be returned.

        Parameters
        ----------
        dtype: string, default=None
            Data type identifier. If given, only objects that match the type
            query string.
        namespace: string, default=None
            Namespace identifier. If given, only objects that match the
            namespace query string.

        Returns
        -------
        list of openclean_jupyter.engine.store.base.ObjectHandle
        """
        # Get list of namespace identifier to filter on. If the user did not
        # specify a namespace all namespace identifier are used.
        ns_query = [namespace] if namespace is not None else list(self._metadata.keys())
        if dtype is not None:
            result = list()
            # Filter on data type if a type query string was given by the user.
            for ns_key in ns_query:
                for obj in self._metadata.get(ns_key).values():
                    if obj.dtype == dtype:
                        result.append(obj)
        else:
            result = [obj for ns_key in ns_query for obj in self._metadata.get(ns_key).values()]
        return result

    def get_object(self, name: str, namespace: Optional[str] = None) -> Dict:
        """Get the seralization for the object that is identified by the given
        name and namespace from the object store. Raises a KeyError if the
        referenced object does not exist.

        Parameters
        ----------
        name: string
            Unique object name.
        namespace: string, default=None
            Optional identifier for the object namespace.

        Returns
        -------
        dict

        Raises
        ------
        KeyError
        """
        # Get the object descriptor and return the associated object
        # serialization. Raises KeyError if the object does not exist.
        return self._metadata.get(namespace, {})[name].get_object()

    def namespaces(self) -> Set[str]:
        """Get list of all defined namespace identifier. Does not include the
        identifier (None) for the global namespace.

        Returns
        -------
        set of string
        """
        return {ns for ns in self._metadata if ns is not None}

    def remove_object(self, name: str, namespace: Optional[str] = None):
        """Remove the object that is identified by the given name and namespace
        from the object store. Raises a KeyError if the referenced object does
        not exist.

        Parameters
        ----------
        name: string
            Unique object name.
        namespace: string, default=None
            Optional identifier for the object namespace.

        Raises
        ------
        KeyError
        """
        # Get the object descriptor. Raises KeyError if the object does not
        # exist.
        obj = self._metadata.get(namespace, {})[name]
        # Update the metadata cache. We first delete the object descriptor. If
        # the namespace is empty after the object was deleted, we delete the
        # namespace as well.
        ns = self._metadata[namespace]
        del ns[name]
        if len(ns) == 0:
            del self._metadata[namespace]
        # Delete the object file on disk after storing the updated metadata.
        self._write_metadata()
        self.store.delete_object(obj.identifier)
        self.store.commit()

    def insert_object(
        self, doc: Dict, name: str, dtype: str, namespace: Optional[str] = None
    ):
        """Store an object serialization under the given name and the optional
        namespace. If an object with the same identifier exists it will be
        replaced by the given object.

        Objects are stored in separate Json files. the file names are generated
        by unique (16 character strings).

        Parameters
        ----------
        doc: dict
            Dictionary serialization for the object.
        name: string
            Unique object name.
        dtype: string
            Unique object data type identifier.
        namespace: string, default=None
            Optional identifier for the object namespace.
        """
        # Get a unique object identifier.
        object_id = unique_identifier(16)
        while self.store.exists_object(object_id):
            object_id = unique_identifier(16)
        # Store the object serialization under the unique key.
        self.store.write_object(object_id, json.dumps(doc, cls=self.encoder))
        # Update the metadata cache and the stored metadata on disk.
        obj = RepoObjectHandle(
            identifier=object_id,
            name=name,
            namespace=namespace,
            dtype=dtype,
            store=self.store,
            decoder=self.decoder
        )
        self._metadata[obj.namespace][obj.name] = obj
        self._write_metadata()
        self.store.commit()

    def types(self) -> Set[str]:
        """Get list of all data type identifier for objects that are currently
        maintained by the object store.

        Returns
        -------
        set of string
        """
        return {obj.dtype for ns in self._metadata.values() for obj in ns.values()}

    def _write_metadata(self):
        """Write the current metadata index to the object store."""
        doc = [obj.to_dict() for ns in self._metadata.values() for obj in ns.values()]
        self.store.write_object(METADATA_FILE, json.dumps(doc))
