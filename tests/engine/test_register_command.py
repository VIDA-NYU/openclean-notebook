# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Unit tests for registering and executing commands via the openclean engine."""


def add_ten(n):
    """Test update function that adds ten to a given argument."""
    return n + 10


def test_register_and__update(volatile_engine, dataset):
    """Test registering and applying a user defined function."""
    volatile_engine.load_dataset(source=dataset, name='DS', primary_key='A')
    volatile_engine.register.eval('addten')(add_ten)
    volatile_engine.apply('DS').addten('B')
    # Validate results.
    # Original dataset.
    df = volatile_engine.checkout('DS', version=0)
    assert list(df['A']) == [1, 3]
    assert list(df['B']) == [2, 4]
    assert list(df['C']) == [3, 5]
    # Updated dataset.
    df = volatile_engine.checkout('DS', version=1)
    assert list(df['A']) == [1, 3]
    assert list(df['B']) == [12, 14]
    assert list(df['C']) == [3, 5]
