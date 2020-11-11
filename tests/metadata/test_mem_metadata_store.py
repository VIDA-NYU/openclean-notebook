# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the volatile metadata store."""

from openclean_jupyter.metadata.metastore.mem import VolatileMetadataStore


def test_read_write_annotations():
    """Test reading and writing metadata objects using the volatile metadata
    store.
    """
    store = VolatileMetadataStore()
    objects = [(None, None), (1, None), (None, 1), (2, None), (1, 2), (2, 3)]
    for column, row in objects:
        # Empty dictionary when accessing object annotations for the first time.
        assert store.read(column_id=column, row_id=row) == dict()
        # Set object annotations and read them again.
        doc = dict({'column': column, 'row': row})
        assert store.write(doc=doc, column_id=column, row_id=row) == doc
        assert store.read(column_id=column, row_id=row) == doc
