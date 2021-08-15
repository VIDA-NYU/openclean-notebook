# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the openclean API extensions of the openclean engine."""

import pkg_resources
import pytest


from openclean_notebook.engine import DB


# -- Mock pkg_resources.resource_string ---------------------------------------

@pytest.fixture
def mock_pkg_resources(monkeypatch):
    """Mock reading the build Javascript files."""
    def mock_read_file(*args, **kwargs):
        if args[1].endswith('.html'):
            return """<html>
            <head>
            </head>
            <body>
                <script>
                {bundle}
                </script>
                <div id="{id}">
                </div>
                <script>
                    opencleanVis.renderOpencleanVisBundle("#{id}", {data});
                </script>
            </body>
            </html>
            """.encode('utf-8')
        else:
            return 'function(){};'.encode('utf-8')

    monkeypatch.setattr(pkg_resources, "resource_string", mock_read_file)


def test_edit_dataset(mock_pkg_resources, dataset, tmpdir):
    """Test to ensure that we can call the edit function without an error."""
    engine = DB(str(tmpdir))
    engine.create(source=dataset, name='DS', primary_key='A')
    engine.edit('DS')
    engine.edit('DS', n=1)


def test_registry_id_collision():
    """Test to ensure that collisions for engine identifier during registration
    are handled properly.
    """
    class IDGenerator:
        def __init__(self):
            self._count = 0

        def __call__(self, length=None):
            self._count += 1
            if self._count < 10:
                return '0'
            else:
                return '1'
    uid = IDGenerator()
    engine_1 = DB(uid=uid)
    assert engine_1.identifier == '0'
    engine_2 = DB(uid=uid)
    assert engine_2.identifier == '1'
