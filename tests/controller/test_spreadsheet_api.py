# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the spreadsheet API."""

from typing import Dict

import pytest

from openclean_jupyter.controller.dataset import DatasetLocator
from openclean_jupyter.controller.spreadsheet import spreadsheet_api
from openclean_jupyter.engine.base import DB

import openclean_jupyter.controller.dataset as ds


# -- Helper functions ---------------------------------------------------------

def request(handle: Dict, payload: Dict) -> Dict:
    r = {'dataset': handle}
    r.update(payload)
    return r


def add_one(n):
    return n + 1


def test_spreadsheet_actions(dataset):
    """Test to ensure that we can call the edit function without an error."""
    engine = DB()
    engine.register.eval('add_one')(add_one)
    engine.create(source=dataset, name='DS', primary_key='A')
    handle = ds.serialize(DatasetLocator(name='DS', engine=engine.identifier))
    # Load dataset and metadata twice. This should ensure that the second
    # request does not call the profiler again.
    for i in range(2):
        doc = spreadsheet_api(request(handle, {'action': 'load'}))
        assert len(doc['columns']) == 3
        assert len(doc['rows']) == 2
        assert doc['rowCount'] == 2
        assert doc['metadata'] is not None
    # Fetch the second row. The response will not include any metadata.
    doc = spreadsheet_api(request(handle, {'action': 'fetch', 'offset': 1}))
    assert len(doc['columns']) == 3
    assert len(doc['rows']) == 1
    doc['rows'][0]['values'] == [3, 4, 5]
    assert doc['rowCount'] == 2
    assert doc['metadata'] is not None
    # Apply the registred update function.
    r = request(
        handle,
        {'action': 'exec', 'command': 'add_one', 'args': {'column': 1}}
    )
    doc = spreadsheet_api(r)
    assert len(doc['columns']) == 3
    assert len(doc['rows']) == 2
    assert doc['rowCount'] == 2
    assert doc['metadata'] is not None
    assert [r['values'][1] for r in doc['rows']] == [3, 5]
    # Error for unknown action.
    with pytest.raises(ValueError):
        spreadsheet_api(request(handle, {'action': 'unknown'}))
