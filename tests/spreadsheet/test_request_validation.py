# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit test for the spreadsheet API request validator."""

from jsonschema.exceptions import ValidationError

import pytest

from openclean_notebook.controller.spreadsheet.base import validator

import openclean_notebook.controller.spreadsheet.data as ds


@pytest.mark.parametrize(
    'action',
    [
        {'type': 'unknown'},
        {'type': 'rollback', 'payload': {'version': '0000'}},
        {'type': 'inscol', 'payload': {'names': [1, 2]}},
        {'type': 'inscol', 'payload': {'names': ['A'], 'args': {'noname': 'X'}}},
        {'type': 'update', 'payload': {'columns': [1]}}
    ]
)
def test_invalid_action_in_requests(action):
    """Test errors when validating a request with an invalid action object."""
    req = {
        'dataset': {'database': 'ABC', 'name': 'XYZ'},
        'fetch': {},
        'action': action
    }
    with pytest.raises(ValidationError):
        validator.validate(req)


@pytest.mark.parametrize('locator', [{}, {'database': 'ABC'}, {'name': 'XYZ'}])
def test_invalid_dataset_in_requests(locator):
    """Test errors when validating a request with invalid dataset locator."""
    req = {'dataset': locator, 'fetch': {}}
    with pytest.raises(ValidationError):
        validator.validate(req)
    with pytest.raises(ValueError):
        ds.deserialize(locator)


@pytest.mark.parametrize(
    'fetch',
    [{'limit': 0}, {'offset': -1}, {'includeMetadata': 1}, {'includeLibrary': 'Yes'}]
)
def test_invalid_fetch_in_requests(fetch):
    """Test errors when validating a request with a invalid fetch query."""
    req = {'dataset': {'database': 'ABC', 'name': 'XYZ'}, 'fetch': fetch}
    with pytest.raises(ValidationError):
        validator.validate(req)


"""Default arguments serialization for evaluation functions."""
ARGS = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': ['A', 'B']}]


@pytest.mark.parametrize(
    'action',
    [
        None,
        {'type': 'commit'},
        {'type': 'inscol', 'payload': {'names': ['A']}},
        {'type': 'inscol', 'payload': {'names': ['A'], 'values': [1], 'args': ARGS, 'sources': [2]}},
        {'type': 'rollback', 'payload': 0},
        {'type': 'update', 'payload': {'columns': [1, 2], 'func': {'name': 'upper'}}},
        {'type': 'update', 'payload': {'columns': [1, 2], 'func': {'name': 'upper'}, 'args': ARGS, 'sources': [2]}}
    ]
)
@pytest.mark.parametrize(
    'fetch',
    [
        {},
        {'limit': 10},
        {'offset': 0},
        {'limit': 1, 'offset': 10},
        {'limit': 1, 'offset': 10, 'includeMetadata': True, 'includeLibrary': False}
    ]
)
def test_valid_requests(action, fetch):
    """Test successful validation of valid requests."""
    req = {'dataset': {'database': 'ABC', 'name': 'XYZ'}, 'fetch': fetch}
    if action is not None:
        req['action'] = action
    validator.validate(req)
