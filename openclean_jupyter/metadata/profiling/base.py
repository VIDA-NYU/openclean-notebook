# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (C) 2018-2020 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

from abc import ABCMeta, abstractmethod

import pandas as pd

from typing import Dict


class Profiler(metaclass=ABCMeta):
    """Interface for data profiler that generate metadata for a given data
    frame.
    """
    @abstractmethod
    def profile(self, df: pd.DataFrame) -> Dict:
        """Run profiler on a given data frame. The structure of the resulting
        dictionary is implementatin dependent.

        TODO: define required components in the result of a data profier.

        Parameters
        ----------
        df: pd.DataFrame
            INput data frame.

        Returns
        -------
        dict
        """
        raise NotImplementedError()  # pragma: no cover
