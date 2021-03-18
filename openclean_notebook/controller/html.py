# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Helper functions to generate embeddable HTML for displaying Javascript UI
components in a Jupyter or Colab notebook.
"""

import json
import pkg_resources
import uuid

from typing import Dict


"""Relative path to the folder containing Javascript libraries and HTML
templates
."""
JAVASCRIPT = '../ui/{}'
TEMPLATES = '../ui/templates/{}'


def make_html(template: str, library: str, data: Dict) -> str:
    """Create HTML string from a given template. The package name references a
    (bundeled) Javascript file containint all required Javascript scripts. The
    script parameter is the name of the main Javascript routine in the package
    that will e called when the HTML loads. The function will receive two
    arguments: (1) the identifier of the element in the DOM where UI components
    should be rendered, and (2) the data dictionary that is passes to this
    function as an argument.

    Parameters
    ----------
    template: string
        Name of the HTML template. This is the path name to a file relative
        to the openclean_notebook/ui/templates folder.
    package: string
        Name of a Javascript package file (build bundle) that contains the
        script that is being embedded into the returned HTML string.
    data: dict
        Dictionary containing data that is being embedded into the returned
        HTML string and passed to the script as the second argument.

    Returns
    -------
    string
    """
    # Read the HTML template and the Javascript bundle file.
    html_template = readfile(TEMPLATES.format(template))
    js_bundle = readfile(JAVASCRIPT.format(library))
    # Generate a unique identifier for the DOM element. Ensure that the
    # identifier does not start with a digit (to avoid 'not a valid selector'
    # exceptions in Javascript).
    id = '_div{}'.format(str(uuid.uuid4()).replace('-', ''))
    # Return the formated template.
    return html_template.format(
        id=id,
        bundle=js_bundle,
        data=json.dumps(data)
    )


def readfile(filename: str) -> str:
    """Read a file that is contained in the openclean_notebook package. This is
    a helper method to read Javascript files and HTML templates that are part
    of the openclean_notebook package.

    Returns a string containing the file contents.

    Parameters
    ----------
    filename: string
        Relative path to the file that is being read.

    Returns
    -------
    string
    """
    return pkg_resources.resource_string(__name__, filename).decode('utf-8')
