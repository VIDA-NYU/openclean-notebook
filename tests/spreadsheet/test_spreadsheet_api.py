# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the spreadsheet API."""

from jsonschema import Draft7Validator, RefResolver
from typing import Dict, Optional

import importlib.resources as pkg_resources
import json
import os
import pytest

from openclean_jupyter.controller.spreadsheet.data import Dataset
from openclean_jupyter.controller.spreadsheet.base import spreadsheet_api
from openclean_jupyter.engine import DB

import openclean_jupyter.controller.spreadsheet as pkg


# -- Helper functions ---------------------------------------------------------

DS_NAME = 'DS'


def request(handle: Dict, payload: Optional[Dict] = None) -> Dict:
    r = {'dataset': handle}
    if payload is not None:
        r.update(payload)
    return r


def add_one_or_some(n: int, value: Optional[int] = 1):
    """Test function that is used to add one or a given number to the values in
    a data frame column.
    """
    return n + value


@pytest.fixture
def engine(dataset):
    """Create an instance of the openclean API."""
    engine = DB()
    engine.register.eval('myadd')(add_one_or_some)
    engine.create(source=dataset, name=DS_NAME, primary_key='A')
    return engine


@pytest.fixture
def validator():
    """Get response validator for Json schema definition of API responses."""
    schemafile = os.path.abspath(os.path.join(pkg.__file__, "schema.json"))
    schema = json.load(pkg_resources.open_text(pkg, 'schema.json'))
    resolver = RefResolver(schemafile, schema)
    return Draft7Validator(schema=schema, resolver=resolver)


# -- Test API calls -----------------------------------------------------------

@pytest.mark.parametrize(
    'payload,offset,values',
    [(None, 0, [1, 3, 5, 7]), ({'limit': 2, 'offset': 1}, 1, [3, 5])]
)
def test_fetch_rows(payload, offset, values, engine, validator):
    """Test fetching rows from the API."""
    # -- Setup --
    handle = Dataset(name=DS_NAME, engine=engine.identifier).serialize()
    # -- Fetch all rows  --
    doc = spreadsheet_api(request(handle, payload=payload))
    validator.validate(doc)
    assert len(doc['columns']) == 3
    assert len(doc['rows']) == len(values)
    assert doc['rowCount'] == 4
    assert doc['offset'] == offset
    assert [r['values'][0] for r in doc['rows']] == values


def test_fetch_rows_with_metadata(engine, validator):
    """Test fetching rows with and without metadata."""
    # -- Setup --
    handle = Dataset(name=DS_NAME, engine=engine.identifier).serialize()
    # -- Fetch all rows  --
    doc = spreadsheet_api(request(handle, payload={'includeMetadata': True}))
    validator.validate(doc)
    assert 'metadata' in doc
    metadata = doc['metadata']
    doc = spreadsheet_api(request(handle, payload={'includeMetadata': False}))
    validator.validate(doc)
    assert 'metadata' not in doc
    doc = spreadsheet_api(request(handle, payload={'includeMetadata': True}))
    validator.validate(doc)
    assert 'metadata' in doc
    assert metadata == doc['metadata']


def test_modify_dataset(engine, validator):
    """Test update and insert operations that modify the dataset."""
    # -- Setup --
    handle = Dataset(name=DS_NAME, engine=engine.identifier).serialize()
    # -- Insert column with constant value at first position --
    payload = {'command': {'names': ['D'], 'pos': 0, 'values': [5]}}
    doc = spreadsheet_api(request(handle, payload=payload))
    validator.validate(doc)
    assert doc['columns'] == ['D', 'A', 'B', 'C']
    assert len(doc['rows']) == 4
    assert 'metadata' in doc
    assert [r['values'][0] for r in doc['rows']] == [5, 5, 5, 5]
    assert [r['values'][1] for r in doc['rows']] == [1, 3, 5, 7]
