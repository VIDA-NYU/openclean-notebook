===============================================
openclean Notebook Environment - User Interface
===============================================

.. image:: https://img.shields.io/pypi/pyversions/openclean-notebook.svg
    :target: https://pypi.org/pypi/openclean-notebook

.. image:: https://badge.fury.io/py/openclean-notebook.svg
    :target: https://badge.fury.io/py/openclean-notebook

.. image:: https://img.shields.io/badge/License-BSD-green.svg
    :target: https://github.com/VIDA-NYU/openclean-notebook/blob/master/LICENSE

.. image:: https://github.com/VIDA-NYU/openclean-notebook/actions/workflows/build.yml/badge.svg
    :target: https://github.com/VIDA-NYU/openclean-notebook/actions/workflows/build.yml

.. image:: https://readthedocs.org/projects/openclean-notebook/badge/?version=latest
    :target: https://openclean-notebook.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/VIDA-NYU/openclean-notebook/branch/master/graph/badge.svg?token=7YRZIGOR1J
    :target: https://codecov.io/gh/VIDA-NYU/openclean-notebook


.. figure:: https://github.com/VIDA-NYU/openclean-notebook/blob/master/docs/graphics/logo.png
    :align: center
    :alt: openclean Logo



About
=====

This package provides a graphical user interface for **openclean** that can be used to visualize and manipulate datasets in notebook environments like Jupyter Notebooks.


Installation
============

The package can be installed using ``pip``.

.. code-block:: bash

    pip install openclean-notebook


You can use the additional ``[jupyter]`` option to install the Python Jupyter package if you want to use the UI within a Jupyter Notebook.

.. code-block:: bash

    pip install openclean-notebook[jupyter]


The notebook UI is a JavaScript bundle that is included in the installed package.


Usage
=====

To use the notebook UI, an instance of the `openclean_notebook.engine.OpencleanAPI <https://github.com/VIDA-NYU/openclean-notebook/blob/master/openclean_notebook/engine.py>`_ is required. The API engine provides a namespace that manages a set of datasets that are identified by unique names. The engine is associated with an object repository that provides additional functionality to register objects like functions, lookup tables, etc.. The engine is also responsible for coordinating the communication with the JavaScript UI.

A helper function to create an instance of the openclean API is included in the ``openclean_notebook`` package. For example:

.. code-block:: python

    from openclean_notebook import DB
    db = DB(basedir='.openclean', create=True)

In this example a new instance of the API engine is created that stores all dataset files in a local folder ``.openclean``. The ``create=True`` flag ensures that a fresh instance is created every time the code (cell) is run.

The next step is to create a new dataset in the API, e.g., from a given data frame or data file. Each dataset has to have a unique name.

.. code-block:: python

    db.load_dataset(source=source='./data/bre9-aqqr.tsv.gz', name='covid-cases')


You can then either view and edit the full dataset using the notebook UI or (e.g., for performance reasons) a sample of the dataset. The recipe that is created from the interactions in the notebook UI can later be applied on the full dataset. In the example below we use a sample of 100 rows for display in the notebook UI.

.. code-block:: python

    db.edit('covid-cases', n=100)


For a full example please have a look at the `example notebook <https://github.com/VIDA-NYU/openclean-notebook/blob/master/examples/notebooks/Openclean%20Goes%20Jupyter%20-%20Example.ipynb>`_ that also shows how to register and run commands on the dataset.
