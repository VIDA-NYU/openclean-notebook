# This file is part of the History Store (histore).
#
# Copyright (C) 2018-2020 New York University.
#
# The History Store (histore) is released under the Revised BSD License. See
# file LICENSE for full license details.

"""Helper class for maintaining metadata information about dataset snapshots.
Metadata for each snapshot is maintained in a separate json file in a folder on
the file system (named .viziermeta). The metadata file contains two main
elements:

  - columns: serialization of the dataset schema
  - annotations: serialization of dataset annotations
"""

import json
import os

from typing import Any, Callable, Dict, Optional

from histore.archive.store.fs.reader import default_decoder
from histore.archive.store.fs.writer import DefaultEncoder
from openclean_jupyter.metadata.metastore.base import MetadataStore

import histore.util as util


class FileSystemMetadataStore(MetadataStore):
    """Metadata store that maintains annotations for a dataset snapshot in JSON
    files with a given base directory. The files that maintain annotations
    are named using the resource identifier. The following are the file names
    of metadata files for different types of resources:

    - ds.json: Dataset annotations
    - col_{column_id}.json: Column annotations
    - row_{row_id}.json: Row annotations
    - cell_{column_id}_{row_id}.json: Dataset cell annotations.
    """
    def __init__(
        self, basedir: str, encoder: Optional[json.JSONEncoder] = None,
        decoder: Optional[Callable] = None
    ):
        """Initialize the base directory and the optional JSON encoder and
        decoder.

        Parameters
        ----------
        basedir: string
            Path to the base directory for all annotation files. The directory
            is created if it does not exist.
        encoder: json.JSONEncoder, default=None
            Encoder for JSON objects.
        decoder: callable: default=None
            Object hook when decoding JSON objects.
        """
        # Create base directory if it does not exist.
        self.basedir = util.createdir(basedir)
        # Use the default decoder if None is given.
        self.decoder = decoder if decoder is not None else default_decoder
        # Use the default JSONEncoder if no encoder is given
        self.encoder = encoder if encoder is not None else DefaultEncoder

    def delete_annotation(
        self, key: str, column_id: Optional[int] = None,
        row_id: Optional[int] = None
    ):
        """Delete annotation with the given key for the object that is
        identified by the given combination of column and row identfier.

        Parameters
        ----------
        key: string
            Unique annotation key.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).
        """
        doc = self.read(column_id=column_id, row_id=row_id)
        if key in doc:
            del doc[key]
        self.write(doc=doc, column_id=column_id, row_id=row_id)

    def get_annotation(
        self, key: str, column_id: Optional[int] = None,
        row_id: Optional[int] = None, default_value: Optional[Any] = None
    ) -> Any:
        """Get annotation with the given key for the identified object. Returns
        the default vlue if no annotation with the given ey exists for the
        object.

        Parameters
        ----------
        key: string
            Unique annotation key.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).
        default_value: any, default=None
            Default value that is returned if no annotation with the given key
            exists for the identified object.

        Returns
        -------
        Any
        """
        doc = self.read(column_id=column_id, row_id=row_id)
        return doc.get(key, default_value)

    def has_annotation(
        self, key: str, column_id: Optional[int] = None,
        row_id: Optional[int] = None
    ) -> bool:
        """Test if an annotation with the given key exists for the identified
        object.

        Parameters
        ----------
        key: string
            Unique annotation key.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).

        Returns
        -------
        bool
        """
        return key in self.read(column_id=column_id, row_id=row_id)

    def list_annotations(
        self, column_id: Optional[int] = None, row_id: Optional[int] = None
    ) -> Dict:
        """Get all annotations for an identified object as a key,value-pair
        dictionary.

        Parameters
        ----------
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).
        """
        return self.read(column_id=column_id, row_id=row_id)

    def read(
        self, column_id: Optional[int] = None, row_id: Optional[int] = None
    ) -> Dict:
        """Read the annotation dictionary for the specified object.

        Parameters
        ----------
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).

        Returns
        -------
        dict
        """
        filename = os.path.join(self.basedir, FILE(column_id, row_id))
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f, object_hook=self.decoder)
        return dict()

    def set_annotation(
        self, key: str, value: Any, column_id: Optional[int] = None,
        row_id: Optional[int] = None
    ):
        """Set annotation value for an identified object.

        Parameters
        ----------
        key: string
            Unique annotation key.
        value: any
            Value that will be associated with the given key.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).
        """
        doc = self.read(column_id=column_id, row_id=row_id)
        doc[key] = value
        self.write(doc=doc, column_id=column_id, row_id=row_id)

    def write(
        self, doc: Dict, column_id: Optional[int] = None,
        row_id: Optional[int] = None
    ):
        """Write the annotation dictionary for the specified object.

        Parameters
        ----------
        doc: dict
            Annotation dictionary that is being written to file.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).

        Returns
        -------
        dict
        """
        filename = os.path.join(self.basedir, FILE(column_id, row_id))
        with open(filename, 'w') as f:
            return json.dump(doc, f, cls=self.encoder)


# -- Helper functions ---------------------------------------------------------

def FILE(column_id: Optional[int] = None, row_id: Optional[int] = None) -> str:
    """Get name for metadata file. The file name depends on whether identifier
    for the column and row are given or not. The following are the file names
    of metadata files for different types of resources:

    - ds.json: Dataset annotations
    - col_{column_id}.json: Column annotations
    - row_{row_id}.json: Row annotations
    - cell_{column_id}_{row_id}.json: Dataset cell annotations.

    Parameters
    ----------
    snapshot_id: int
        Unique snapshot version identifier.
    metadata_id: int
        Unique metadata object identifier.

    Returns
    -------
    string
    """
    if column_id is None and row_id is None:
        return 'ds.json'
    elif row_id is None:
        return 'col_{}.json'.format(column_id)
    elif column_id is None:
        return 'row_{}.json'.format(row_id)
    return 'cell_{}_{}.json'.format(column_id, row_id)
