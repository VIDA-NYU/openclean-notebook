# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""General fixtures for unit tests."""

import pandas as pd
import pytest


@pytest.fixture
def dataset():
    """Returns a basic data frame with three columns and four rows."""
    return pd.DataFrame(
        data=[[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 9]],
        columns=['A', 'B', 'C']
    )
