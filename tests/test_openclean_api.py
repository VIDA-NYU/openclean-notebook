# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the openclean API extensions of the openclean engine."""

from openclean_notebook.engine import DB


def test_edit_dataset(dataset, tmpdir):
    """Test to ensure that we can call the edit function without an error."""
    engine = DB(str(tmpdir))
    engine.create(source=dataset, name='DS', primary_key='A')
    engine.edit('DS')
    engine.edit('DS', n=1)
