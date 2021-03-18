# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Helper classes for accessing datasets as part of requests from components
that are rendered in a notebook environment.
"""

from __future__ import annotations
from typing import Dict, List, Tuple

import pandas as pd

from openclean.engine.dataset import DatasetHandle
from openclean.engine.registry import registry
from openclean_notebook.engine import OpencleanAPI
from openclean_notebook.metadata.datamart import DatamartProfiler


# -- Dataset locator (de)serialization ----------------------------------------

def deserialize(doc: Dict) -> Tuple[DatasetHandle, OpencleanAPI]:
    """Extract the dataset name and engine identifier from the dataset
    locator in a request body. Expects a dictionary with two elements:
    'name' for the dataset name and 'engine' for the engine identifier.

    The document may be None. Raises a ValueError if an invalid dictionary
    is given.

    Parameters
    ----------
    doc: dict
        Dictionary containing dataset name and engine identifier.

    Returns
    -------
    tuple of openclean.engine.data.DatasetHandle, openclean_notebook.engine.OpencleanAPI

    Raises
    ------
    ValueError
    """
    if not doc or len(doc) > 2:
        raise ValueError('invalid dataset locator')
    if 'name' not in doc:
        raise ValueError('missing name in dataset locator')
    if 'database' not in doc:
        raise ValueError('missing database identifier in dataset locator')
    engine = registry.get(doc['database'])
    return engine.dataset(doc['name']), engine


def serialize(name: str, engine: str) -> Dict:
    """Get dictionary serialization for a dataset locator.

    Parameters
    ----------
    name: string
        Unique dataset name.
    engine: string
        Unique identifier of the database engine (API).

    Returns
    -------
    dict
    """
    return {'name': name, 'database': engine}


# -- Fetch serialized dataset objects -----------------------------------------

def fetch_metadata(df: pd.DataFrame, dataset: DatasetHandle) -> Dict:
    """Get metadata for the given dataset. Returns an object that contains
    profiling results and a serialization of the operation log.

    Parameters
    ----------
    df: pd.DataFrame
        Data frame for the dataset snapshot.
    dataset: openclean.engine.data.DatasetHandle
        Handle for the dataset that provides access to the metadata store and
        the operation log.
    """
    metadata = dataset.metadata()
    if not metadata.has_annotation(key='profiling'):
        # We only need to invoke the profiler if the profiling metadata
        # does not already exists for the dataset snapshot.
        profiles = DatamartProfiler().profile(df)
        metadataJSON = {
            'id': dataset.version(),
            'name': '',
            'description': '',
            'size': profiles['size'] if 'size' in profiles else 0,
            'nb_rows': profiles['nb_rows'],
            'nb_profiled_rows': profiles['nb_profiled_rows'],
            'materialize': {},
            'date': '',
            'sample': profiles['sample'] if 'sample' in profiles else '',
            'source': 'openclean-notebook',
            'version': '0.1',
            'columns': profiles['columns'],
            'types': profiles['types']
        }
        metadata.set_annotation(
            key='profiling',
            value=metadataJSON
        )
    else:
        # Use metadata from previous profiler run.
        metadataJSON = metadata.get_annotation(key='profiling')
    # Add profiler results and serialization of the operation log to the
    # returned metadata object.
    return {
        'profiling': metadataJSON,
        'log': [{
            'id': e.version,
            'op': e.descriptor,
            'isCommitted': False
        } for e in dataset.log()]
    }


def fetch_rows(df: pd.DataFrame, offset: int, end: int) -> List[Dict]:
    """Get serialization of data frame rows.

    Parameters
    ----------
    df: pd.DataFrame
        Data frame for dataset snapshot.
    offset: int
        Offset for first row in the returned result.
    end: int
        Index for first row that is not in the returned result.

    Returns
    -------
    list of dict
    """
    return [{'id': id, 'values': list(vals)} for id, vals in df[offset:end].iterrows()]
