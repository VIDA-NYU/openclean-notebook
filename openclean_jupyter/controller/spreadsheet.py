# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Request handler for the spreadsheet view in the notebook."""

from typing import Dict, Optional

from openclean.data.types import Column

from openclean_jupyter.controller.dataset import DatasetLocator
from openclean_jupyter.controller.comm import register_handler
from openclean_jupyter.controller.html import make_html
from openclean_jupyter.metadata.profiling.datamart import DatamartProfiler

import openclean_jupyter.controller.dataset as ds


"""Default number of rows returned by a fetch request."""
DEFAULT_LIMIT = 10


# -- Request handlers ---------------------------------------------------------

def spreadsheet_api(request: Dict) -> Dict:
    """Handler for requests of the spreadsheet view in notebooks. Expects a
    dictionary that contains at least an 'action' and a 'dataset' element. The
    dataset element contains a serialization of the dataset locator with the
    following two fields:

    - name: Unique dataset name
    - engine: Unique engine identifier (for the engine instance that manages
      the dataset).

    The action value can be one of the following values:

    - exec: Execute a command on a given dataset. Additional elements in the
      request are 'command' containing the unique command identifier and the
      command-specific dictionary of command arguments 'args'.
    - fetch: Fetch a number of rows from a dataset. Additional elements are
      'limit' to specify the number of rows that are fetched and 'offset' that
      specifies the index of the firt row that is being fetched.
    - load: Get the first n rows in a specified dataset as well as the list
      of available commands.

    Parameters
    ----------
    request: dict
        Request data.

    Returns
    -------
    dict
    """
    # Get the dataset locator. This will raise an error if the locator is
    # invalid or not present.
    dataset = ds.deserialize(request.get('dataset'))
    # Ensure that the action element specifies a valid action.
    action = request.get('action', 'null')
    if action == 'load':
        # Get result dictionary containing the dataset locator and the dataset
        # columns and rows.
        return fetch_rows(dataset)
    elif action == 'fetch':
        return fetch_rows(
            dataset=dataset,
            limit=request.get('limit', DEFAULT_LIMIT),
            offset=request.get('offset', 0),
            include_metadata=False
        )
    elif action == 'exec':
        dataset = dataset.exec(
            cmd=request.get('command'),
            args=request.get('args')
        )
        return fetch_rows(dataset)
    raise ValueError("unknown action '{}'".format(action))


def fetch_rows(
    dataset: DatasetLocator, limit: Optional[int] = DEFAULT_LIMIT,
    offset: Optional[int] = 0, include_metadata: Optional[bool] = True
) -> Dict:
    """Fetch limited number of rows from a dataset. Returns a serialization of
    the columns in the dataset schema and the fetched rows. The result has the
    following schema:

    - dataset:
      - name: string
        engine: string
    - columns:
      - id: int
        name: string
    - rows:
      - id: int
        values: []
    - offset: int
    - rowCount: int

    Parameters
    ----------
    dataset: openclean_jupyter.controller.base.DatasetLocator
        Locator for dataset for which rows are being fetched.
    limit: int, default=10
        Maximum number of rows that are being fetched.
    offset: int, default=0
        Index of the first row that is being fetched.
    include_metadata: bool, default=True
        Flag to determine whether to include profiling metadata in the response
        or not .

    Returns
    -------
    dict
    """
    # Load the latest snapshot of the referenced dataset.
    df = dataset.load()
    # Create serialization of the dataset schema.
    columns = list()
    for col in df.columns:
        if isinstance(col, Column):
            columns.append({'id': col.colid, 'name': col})
        else:
            columns.append({'id': -1, 'name': col})

    # Get metadata using datamart-profiler. TODO: add support for other data
    # profiler.
    metadataJSON = {}
    if include_metadata:
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
            # use metadata from previous profiler run.
            metadataJSON = metadata.get_annotation(key='profiling')
    # Serialize dataset rows.
    row_count = df.shape[0]
    end = min(offset + limit, row_count)
    rows = list()
    for rid, values in df[offset:end].iterrows():
        rows.append({'id': rid, 'values': list(values)})
    # For now we also add the command listing to the respose. That should
    # disapear in the future.
    return {
        'dataset': ds.serialize(dataset),
        'columns': columns,
        'rows': rows,
        'offset': offset,
        'rowCount': row_count,
        'commands': dataset.commands(),
        'metadata': metadataJSON
    }


# -- Spreadsheet controller ---------------------------------------------------

def spreadsheet(name: str, engine: str):
    """Embed the spreadsheet view for a given dataset into the notebook
    environment.

    Parameters
    ----------
    name: string
        Unique dataset name.
    engine: string
        Unique engine identifier.
    """
    # Register callback handlers. This will raise a RuntimeError if called
    # outside a Jupyter or Colab notebook environment.
    register_handler('spreadsheet', spreadsheet_api)
    # Embed the spreadsheet HTML into the notebook.
    from IPython.core.display import display, HTML
    view = make_html(
            template='spreadsheet.html',
            library='build/opencleanVis.js',
            data=ds.serialize(DatasetLocator(name=name, engine=engine))
        )
    display(HTML(view))
