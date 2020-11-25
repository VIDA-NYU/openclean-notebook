# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Request handler for the spreadsheet view in the notebook."""

from jsonschema import Draft7Validator, RefResolver
from typing import Dict

import importlib.resources as pkg_resources
import json
import os

from openclean_jupyter.controller.comm import register_handler
from openclean_jupyter.controller.html import make_html
from openclean_jupyter.controller.spreadsheet.data import Dataset
from openclean_jupyter.metadata.datamart import DatamartProfiler


"""Create schema validator for API requests."""
schemafile = os.path.abspath(os.path.join(__file__, 'schema.json'))
schema = json.load(pkg_resources.open_text(__package__, 'schema.json'))
resolver = RefResolver(schemafile, schema)
validator = Draft7Validator(schema=schema['definitions']['request'], resolver=resolver)


"""Default number of rows returned by a fetch request."""
DEFAULT_LIMIT = 10


# -- Request handler ----------------------------------------------------------

def spreadsheet_api(request: Dict) -> Dict:
    """Handler for requests of the spreadsheet view in notebooks. Expects a
    dictionary that adheres to the following schema (see `schema.json` for the
    full Json Schema definition):

    ```
    dependencies:
      command:
      - columns
    description: General structure for requests that are handled by the spreadsheet API
    properties:
      args:
        description: List of key-value pairs for additional function arguments
        items:
          properties:
            name:
              description: Unique argument name
              type: string
            value:
              oneOf:
              - type: number
              - type: string
              - type: object
              - type: array
          type: object
        type: array
      columns:
        description: List of index positions for columns that are targets (and potentially
          sources) for the evaluation function
        items:
          type: integer
        type: array
      command:
        description: Definition of executed command
        properties:
          name:
            description: Unique name for registered evaluation function
            type: string
          namespace:
            description: Optional namespace identifier
            type: string
          optype:
            description: Identifier for type of action (insert or update)
            enum:
            - ins
            - upd
            type: string
        required:
        - optype
        - name
        type: object
      dataset:
        description: Identifier for the dataset that is being accessed
        properties:
          database:
            description: Identifier of the database engine that manages the dataset
            type: string
          name:
            description: Unique dataset name
            type: string
        required:
        - database
        - name
        type: object
      includeMetadata:
        description: Include profiling metadata in the response if true
        type: boolean
      limit:
        description: Maximum number of rows in the response
        minimum: 1
        type: integer
      offset:
        description: Offset for first row in the response
        minimum: 0
        type: integer
      sources:
        description: List of index positions for alternative input columns
        items:
          type: integer
        type: array
    required:
    - dataset
    type: object
    ```

    The 'dataset' element contains a serialization of the dataset locator.
    Datasets are identified by their unique name and the identifier of the
    database engine that maintains them.

    The type of the action that is being performed depends on the presence (or
    absence) or the 'command' element. If a command is specified the dataset is
    being modified by the given command. If no command is specified rows for
    from the dataset are fetched. Fr a fetch operation only the 'limit', 'offset',
    and 'includeMetadata' elements are considered.

    Parameters
    ----------
    request: dict
        Request data.

    Returns
    -------
    dict
    """
    # Validate the given request against the API request schema.
    validator.validate(request)
    # Get the dataset locator. This will raise an error if the locator is
    # invalid or not present.
    dataset = Dataset.deserialize(request.get('dataset'))
    # Depending on whether the command element is present or not the dataset is
    # either modified or rows from the dataset are being fetched.
    if 'command' in request:
        # Note that for an evaluation command we return the metadata of the
        # created dataset snapshot by default. The argument is that the metadata
        # may have changed as a result of the modification operation.
        return eval_command(
            dataset=dataset,
            command=request['command'],
            limit=request.get('limit', DEFAULT_LIMIT),
            offset=request.get('offset', 0),
            include_metadata=request.get('includeMetadata', True)
        )
    else:
        # Note that for a nor mal fetch operation the dataset metadata is not
        # included in the response. The argument here is that the metadata does
        # not change inbetween fetch operations (i.e., only needs to be read
        # as part of the first fetch request).
        return fetch_rows(
            dataset=dataset,
            limit=request.get('limit', DEFAULT_LIMIT),
            offset=request.get('offset', 0),
            include_metadata=request.get('includeMetadata', False)
        )


# -- API operations -----------------------------------------------------------

def eval_command(
    dataset: Dataset, command: Dict, limit: int, offset: int, include_metadata: bool
) -> Dict:
    """Evaluate a command on a given dataset. The command dictionary contains
    the type of action ('insert' or 'update') and the evaluation function. The
    function has to be a function that is registered with the object repository
    for the database engine of the dataset. The list of arguments are dictionaries
    of key-value pairs for function-specific arguments.

    Returns the engine for the updated dataset snapshot.

    Raises a ValueError if (i) no command identifier is given, (ii) the
    command identifier is unknown, or (iii) the given argument values do
    not satisfy the parameter constraints of the selected command.

    Parameters
    ----------
    dataset: openclean_jupyter.controller.spreadsheet.data.Dataset
        Dataset that is being modified.
    command: dict
        Definition of the command that is being executed.
    limit: int, default=10
        Maximum number of rows that are being returned in the response.
    offset: int, default=0
        Index of the first row that is being returned in the response.
    include_metadata: bool, default=True
        Flag to determine whether to include profiling metadata in the response
        or not .

    Returns
    -------
    dict

    Raises
    ------
    ValueError
    """
    # The type of the operations is currently distinguished between insert and
    # update based on the presence of the 'names' or 'columns' element.
    if 'names' in command:
        dataset.insert(
            names=command.get('names'),
            pos=command.get('pos'),
            values=command.get('values'),
            args=command.get('args'),
            sources=command.get('sources')
        )
    elif 'columns' in command:
        dataset.update(
            columns=command.get('columns'),
            func=command.get('func'),
            args=command.get('args'),
            sources=command.get('sources')
        )
    else:
        raise ValueError("unknown operation '{}'".format(command))
    return fetch_rows(
        dataset=dataset,
        limit=limit,
        offset=offset,
        include_metadata=include_metadata
    )


def fetch_rows(dataset: Dataset, limit: int, offset: int, include_metadata: bool) -> Dict:
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
    dataset: openclean_jupyter.controller.spreadsheet.data.Dataset
        Dataset for which rows are being fetched.
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
    df = dataset.checkout()
    # Serialize dataset rows.
    row_count = df.shape[0]
    end = min(offset + limit, row_count)
    rows = list()
    for rid, values in df[offset:end].iterrows():
        rows.append({'id': rid, 'values': list(values)})
    # Create response document.
    doc = {
            'dataset': dataset.serialize(),
            'columns': list(df.columns),
            'rows': rows,
            'offset': offset,
            'rowCount': row_count
        }
    # Add metadata to response if the include_metadata flag is True
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
        doc['metadata'] = metadataJSON
    # Return fetch_rows response.
    return doc


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
    view = make_html(
            template='spreadsheet.html',
            library='build/opencleanVis.js',
            data=Dataset(name=name, engine=engine).serialize()
        )
    # Embed the spreadsheet HTML into the notebook.
    try:
        from IPython.core.display import display, HTML
        display(HTML(view))
    except ImportError:
        pass
