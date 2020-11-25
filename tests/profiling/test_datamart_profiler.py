# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for the datamart profiler."""

from openclean_jupyter.metadata.datamart import DatamartProfiler


def test_profile_dataset(dataset):
    """Test profiling a given dataset."""
    # Profile the full dataset.
    profile = DatamartProfiler().profile(dataset)
    assert len(profile['columns']) == 3
    # Profile only two columns of the dataset.
    profile = DatamartProfiler().profile(dataset, columns=['A', 'C'])
    assert len(profile['columns']) == 2
    assert profile['attribute_keywords'] == ['A', 'C']
