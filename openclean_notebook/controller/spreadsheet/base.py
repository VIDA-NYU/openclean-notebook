# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Request handler for the spreadsheet view in the notebook."""

from flowserv.service.run.argument import deserialize_arg
from jsonschema import Draft7Validator, RefResolver
from typing import Any, Dict, List, Tuple

import importlib.resources as pkg_resources
import json
import os


from openclean_notebook.controller.comm import register_handler
from openclean_notebook.controller.html import make_html
from openclean_notebook.engine import OpencleanAPI

import openclean_notebook.controller.spreadsheet.data as ds


"""Create schema validator for API requests."""
# Make sure that the path to the schema file is a valid URI. Otherwise, errors
# occur (at least on MS Windows environments). Changed based on:
# https://github.com/Julian/jsonschema/issues/398#issuecomment-385130094
schemafile = 'file:///{}'.format(os.path.abspath(os.path.join(__file__, 'schema.json')))
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

    .. code-block:: yaml

        request:
            type: object
            properties:
              action:
                oneOf:
                - $ref: '#/definitions/actionCommit'
                - $ref: '#/definitions/actionInsert'
                - $ref: '#/definitions/actionRollback'
                - $ref: '#/definitions/actionUpdate'
              dataset:
                $ref: '#/definitions/datasetRef'
              fetch:
                properties:
                  includeLibrary:
                    type: boolean
                  includeMetadata:
                    type: boolean
                  limit:
                    minimum: 1
                    type: integer
                  offset:
                    minimum: 0
                    type: integer
                type: object
            required:
            - dataset
            - fetch

    Each request contains at least (i) the reference to the dataset that is being
    displayed in the spreadsheet view and (ii) the query parameters that determine
    the information that is expected in the returned response.

    The 'dataset' element contains a serialization of the dataset locator.
    Datasets are identified by their unique name and the identifier of the
    database engine that maintains them.

    The request may contain an optional 'action' element. The action defines an
    opertation that is applied to the dataset before returning data from the
    modified dataset. The API supports four different actions (identified by the
    'type' element in the action object):

    - commit:   apply all uncommitted changes to the full dataset. This action
                is only available for datasets that are samples of a larger
                dataset. The commit will execute all operations that were
                previously applied to the sample on the full dataset.
    - inscol:   Insert one or multiple columns into the dataset. The additional
                'payload' object specifies the new column names, the insert
                positions, and default values for the inserted columns.
    - rollback: Rollback uncommitted changes. Like the commit, this action is
                only available for datasets that are samples of a larger dataset.
                The 'payload' element contains the target dataset version identifier
                for the rollback. The rollback will undo all changes that result
                from operations in the dataset history that occurred at and
                after the target version.
    - update:   Update one or multiple columns in the dataset. The additional
                'payload' object specifies the updated columns and the function
                (or constants) that generates the updated column values.

    Each request will return at least the dataset schema and a subset of the
    dataset rows. The maximum nuber of rows in the response is controlled by the
    'limit' parameter . The default is defined by the DEFAULT_LIMIT variable. In
    the future we may want to introduce an environment variable for this.

    The response will contain additional metadata if (i) the 'includeMetadata'
    flag is set to True or if an action is performed that modifies the dataset.
    Metadata includes the results of a data profiler as well as the list of
    uncommitted actions (only if the dataset is a sample of a larger dataset).
    In addition, the request can contain the 'includeLibrary' flag in order to
    obtain a list of registered commands (evaluation functions) that can be
    applied to the dataset.

    Parameters
    ----------
    request: dict
        Request body.

    Returns
    -------
    dict
    """
    # Validate the given request against the API request schema.
    validator.validate(request)
    # Get the dataset handle and API engine.
    dataset, engine = ds.deserialize(request['dataset'])
    # If the action element is present we first apply the specified operation on
    # the dataset before returning data from the (modified) dataset.
    action = request.get('action')
    if action is not None:
        action_type = action['type']
        payload = action.get('payload')
        if action_type == 'commit':
            dataset.apply()
        elif action_type == 'inscol':
            values, args = get_eval(
                engine=engine,
                func=payload.get('values'),
                args=payload.get('args')
            )
            dataset.insert(
                names=payload.get('names'),
                pos=payload.get('pos'),
                values=values,
                args=args,
                sources=payload.get('sources')
            )
        elif action_type == 'rollback':
            dataset.rollback(payload)
        else:  # action_type == 'update'
            func, args = get_eval(
                engine=engine,
                func=payload.get('func'),
                args=payload.get('args')
            )
            dataset.update(
                columns=payload.get('columns'),
                func=func,
                args=args,
                sources=payload.get('sources')
            )
    # Return data from the (modified) dataset. Note that by default metadata is
    # included in the response if the request contained an action element that
    # modified the underlying dataset (and therefore the dataset metadata may
    # have changed as well).
    fetch = request['fetch']
    limit = fetch.get('limit', DEFAULT_LIMIT)
    offset = fetch.get('offset', 0)
    version = fetch.get('version')
    include_metadata = fetch.get('includeMetadata', action is not None)
    include_library = fetch.get('includeLibrary', False)
    # Load the requested snapshot of the referenced dataset. If a version number
    # was included in the request we load the data for that version. Otherwise,
    # the data for the latest snapshot is loaded.
    df = dataset.checkout(version=version)
    # Create basic response document.
    row_count = df.shape[0]
    doc = {
            'dataset': request['dataset'],
            'columns': list(df.columns),
            'rows': ds.fetch_rows(
                df=df,
                offset=offset,
                end=min(offset + limit, row_count)
            ),
            'offset': offset,
            'rowCount': row_count,
            'version': version
        }
    # Add metadata to response if the include_metadata flag is True.
    if include_metadata:
        doc['metadata'] = ds.fetch_metadata(df=df, dataset=dataset)
    # Add serialization of registered evaluation functions if requested.
    if include_library:
        doc['library'] = engine.library_dict()
    return doc


def get_eval(engine: OpencleanAPI, func: Any, args: List[Dict]) -> Tuple[Any, Dict]:
    """Get evaluation function handle or scalar value from a specification for
    and update function or value generator for inserted columns. If the func
    argument is for a function handle the argument list is validated against
    the function parameters and converted into a dictionary.

    Parameters
    ----------
    engine: openclean_notebook.engine.OpencleanAPI
        Engine that contains the library of registered functions.
    func: any
        Specification for an evaluation function (dict) or constant scalar
        value.
    args: list of dict
        List of optional argument values. The given value may be None.
    Returns
    -------
    tuple of any, dict
    """
    if isinstance(func, dict):
        # If the specification is a dictionary we assume that it is the
        # serialization of a functin handle identifier.
        namespace = func.get('namespace') if func.get('namespace') else None
        f = engine.library.functions().get(name=func['name'], namespace=namespace)
        # Convert arguments into a dictionary.
        func_args = None
        if args is not None:
            func_args = dict()
            # Map parameter names to parameter declarations.
            paras = {p.name: p for p in f.parameters}
            for arg in args:
                arg_id, arg_val = deserialize_arg(arg)
                para = paras.get(arg_id)
                if para is None:
                    raise ValueError("unknown parameter '{}'".format(arg_id))
                func_args[arg_id] = para.cast(arg_val)
        return f, func_args
    # For any other value we return the function specification (assumed to be a
    # scalar constant at this point) and the arguments as is.
    return func, args


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
            data=ds.serialize(name=name, engine=engine)
        )
    # Embed the spreadsheet HTML into the notebook.
    try:  # pragma: no cover
        from IPython.core.display import display, HTML
        display(HTML(view))
    except ImportError:
        pass
