# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit test for the spreadsheet API request validator."""

from jsonschema.exceptions import ValidationError

import pytest

from openclean_jupyter.controller.spreadsheet.base import validator


@pytest.mark.parametrize(
    'payload',
    [
        {'limit': 0},
        {'offset': -1},
        {'limit': -1, 'offset': 10},
        {'command': {'action': 'upd', 'func': {'name': 'upper'}}}
    ]
)
def test_invalid_requests(payload):
    """Test errors when attempting to validate invalid requests."""
    req = dict(payload)
    req['dataset'] = {'database': 'ABC', 'name': 'XYZ'}
    with pytest.raises(ValidationError):
        validator.validate(req)


@pytest.mark.parametrize(
    'payload',
    [
        {},
        {'limit': 10},
        {'offset': 0},
        {'limit': 1, 'offset': 10},
        {'command': {'names': ['A'], 'values': {'name': 'upper'}}},
        {'command': {'names': ['A'], 'values': 5}},
        {
            'command': {'columns': [1], 'func': {'name': 'upper', 'namespace': 'ns'}},
            'args': [
                {'name': 'X', 'value': 'Y'},
                {'name': 'X', 'value': 1},
                {'name': 'X', 'value': {'key': 'value'}},
                {'name': 'X', 'value': [1, 2, 3]}
            ],
            'sources': [2, 3],
            'limit': 1,
            'offset': 10,
            'includeMetadata': True
        }
    ]
)
def test_valid_requests(payload):
    """Test successful validation of valid requests."""
    req = dict(payload)
    req['dataset'] = {'database': 'ABC', 'name': 'XYZ'}
    validator.validate(req)
