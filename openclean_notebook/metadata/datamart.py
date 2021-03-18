# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.


from typing import Dict, Optional

import datamart_profiler as dmp
import pandas as pd

from openclean.data.types import Columns
from openclean.operator.transform.select import select
from openclean.profiling.dataset import Profiler


class DatamartProfiler(Profiler):
    """Profiler interface implementation for the datamart profiler."""
    def profile(self, df: pd.DataFrame, columns: Optional[Columns] = None) -> Dict:
        """Run profiler on a given data frame. Ensure to create a new data frame
        first that has the row index reset.

        Parameters
        ----------
        df: pd.DataFrame
            Input data frame.
        columns: int, string, or list(int or string), default=None
            Single column or list of column index positions or column names for
            those columns that are being profiled. Profile the full dataset if
            None.

        Returns
        -------
        dict
        """
        # Filter columns if list of columns is given. Otherwise project on all
        # columns in the schema to get a new data frame where we can securely
        # reset the row index.
        columns = list(range(len(df.columns))) if columns is None else columns
        df = select(df=df, columns=columns).reset_index(drop=True)
        return dmp.process_dataset(df, include_sample=False, plots=True)
