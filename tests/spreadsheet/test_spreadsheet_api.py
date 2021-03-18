# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
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

from openclean.engine.object.function import Int

from openclean_notebook.controller.spreadsheet.base import spreadsheet_api
from openclean_notebook.engine import DB

import openclean_notebook.controller.spreadsheet as pkg
import openclean_notebook.controller.spreadsheet.data as ds


# -- Helper functions ---------------------------------------------------------

DS_NAME = 'DS'


def request(handle: Dict, fetch: Dict, action: Optional[Dict] = None) -> Dict:
    r = {'dataset': handle, 'fetch': fetch}
    if action is not None:
        r['action'] = action
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
    para = Int('value', default=1)
    engine.register.eval('myadd', namespace='mylib', parameters=[para])(add_one_or_some)
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
    'fetch,offset,values',
    [({}, 0, [1, 3, 5, 7]), ({'limit': 2, 'offset': 1}, 1, [3, 5])]
)
def test_fetch_rows(fetch, offset, values, engine, validator):
    """Test fetching rows from the API."""
    # -- Setup --
    handle = ds.serialize(name=DS_NAME, engine=engine.identifier)
    # -- Fetch all rows  --
    doc = spreadsheet_api(request(handle, fetch=fetch))
    validator.validate(doc)
    assert len(doc['columns']) == 3
    assert len(doc['rows']) == len(values)
    assert doc['rowCount'] == 4
    assert doc['offset'] == offset
    assert [r['values'][0] for r in doc['rows']] == values


def test_fetch_rows_with_metadata(engine, validator):
    """Test fetching rows with and without metadata."""
    # -- Setup --
    handle = ds.serialize(name=DS_NAME, engine=engine.identifier)
    # -- Fetch all rows  with metadata (but without library) --
    doc = spreadsheet_api(request(handle, fetch={'includeMetadata': True}))
    validator.validate(doc)
    assert 'metadata' in doc
    assert 'library' not in doc
    metadata = doc['metadata']
    # -- Fetch without metadata --
    doc = spreadsheet_api(request(handle, fetch={'includeMetadata': False}))
    validator.validate(doc)
    assert 'metadata' not in doc
    # -- Fetch with metadata and library --
    doc = spreadsheet_api(
        request(handle, fetch={'includeMetadata': True, 'includeLibrary': True})
    )
    validator.validate(doc)
    assert 'metadata' in doc
    assert 'library' in doc
    assert metadata == doc['metadata']


def test_modify_dataset(engine, validator):
    """Test update and insert operations that modify the dataset."""
    # -- Setup --
    handle = ds.serialize(name=DS_NAME, engine=engine.identifier)
    # -- Insert column with constant value at first position --
    action = {'type': 'inscol', 'payload': {'names': ['D'], 'pos': 0, 'values': [5]}}
    doc = spreadsheet_api(request(handle, fetch={}, action=action))
    validator.validate(doc)
    assert doc['columns'] == ['D', 'A', 'B', 'C']
    assert len(doc['rows']) == 4
    assert 'metadata' in doc
    assert [r['values'][0] for r in doc['rows']] == [5, 5, 5, 5]
    assert [r['values'][1] for r in doc['rows']] == [1, 3, 5, 7]
    # -- Update values in column 'B' using add_one_or_some with default --
    action = {
        'type': 'update',
        'payload': {
            'columns': [2],
            'func': {'name': 'myadd', 'namespace': 'mylib'}
        }
    }
    doc = spreadsheet_api(request(handle, fetch={}, action=action))
    validator.validate(doc)
    assert doc['columns'] == ['D', 'A', 'B', 'C']
    assert len(doc['rows']) == 4
    assert 'metadata' in doc
    assert len(doc['metadata']['log']) == 3
    assert [r['values'][0] for r in doc['rows']] == [5, 5, 5, 5]
    assert [r['values'][2] for r in doc['rows']] == [3, 5, 7, 9]
    # -- Update values in column 'D' by adding the value of 10 --
    action = {
        'type': 'update',
        'payload': {
            'columns': [0],
            'func': {'name': 'myadd', 'namespace': 'mylib'},
            'args': [{'name': 'value', 'value': 10}]
        }
    }
    doc = spreadsheet_api(request(handle, fetch={}, action=action))
    validator.validate(doc)
    assert doc['columns'] == ['D', 'A', 'B', 'C']
    assert len(doc['rows']) == 4
    assert 'metadata' in doc
    assert len(doc['metadata']['log']) == 4
    assert [r['values'][0] for r in doc['rows']] == [15, 15, 15, 15]


def test_rollback_and_commit(engine, validator):
    """Test rollback and commit for an updated sample of a dataset."""
    # -- Setup (create sample with two uncommitted operations) --
    engine.sample(name=DS_NAME, n=2, random_state=42)
    handle = ds.serialize(name=DS_NAME, engine=engine.identifier)
    action = {'type': 'inscol', 'payload': {'names': ['D'], 'pos': 0, 'values': [5]}}
    spreadsheet_api(request(handle, fetch={}, action=action))
    action = {
        'type': 'update',
        'payload': {
            'columns': [2],
            'func': {'name': 'myadd', 'namespace': 'mylib'}
        }
    }
    doc = spreadsheet_api(request(handle, fetch={}, action=action))
    assert len(doc['rows']) == 2
    log = doc['metadata']['log']
    assert len(log) == 3
    values = [r['values'][2] for r in doc['rows']]
    # -- Rollback the last operation --
    action = {'type': 'rollback', 'payload': log[1]['id']}
    doc = spreadsheet_api(request(handle, fetch={}, action=action))
    log = doc['metadata']['log']
    assert len(log) == 2
    assert values == [r['values'][2] + 1 for r in doc['rows']]
    # -- Commit remaining changes to full dataset --
    action = {'type': 'commit'}
    doc = spreadsheet_api(request(handle, fetch={}, action=action))
    assert len(doc['columns']) == 4
    assert [r['values'][0] for r in doc['rows']] == [5, 5]
    log = doc['metadata']['log']
    assert len(log) == 2
    # -- Checkout the full dataset --
    df = engine.checkout(name=DS_NAME)
    assert list(df.columns) == ['D', 'A', 'B', 'C']
    assert list(df['D']) == [5, 5, 5, 5]
