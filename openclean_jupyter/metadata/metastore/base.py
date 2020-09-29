# This file is part of the History Store (histore).
#
# Copyright (C) 2018-2020 New York University.
#
# The History Store (histore) is released under the Revised BSD License. See
# file LICENSE for full license details.

from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional


class MetadataStore(metaclass=ABCMeta):  # pragma: no cover
    """Interface for metadata stores that maintain annotations for individual
    snapshots (datasets) in an archive.
    """
    @abstractmethod
    def delete_annotation(
        self, key: str, column_id: Optional[int] = None,
        row_id: Optional[int] = None
    ):
        """Delete annotation with the given key for the object that is
        identified by the given combination of column and row identfier.

        Parameters
        ----------
        key: string
            Unique annotation key.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).
        """
        raise NotImplementedError()

    @abstractmethod
    def get_annotation(
        self, key: str, column_id: Optional[int] = None,
        row_id: Optional[int] = None, default_value: Optional[Any] = None
    ) -> Any:
        """Get annotation with the given key for the identified object. Returns
        the default vlue if no annotation with the given ey exists for the
        object.

        Parameters
        ----------
        key: string
            Unique annotation key.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).
        default_value: any, default=None
            Default value that is returned if no annotation with the given key
            exists for the identified object.

        Returns
        -------
        Any
        """
        raise NotImplementedError()

    @abstractmethod
    def has_annotation(
        self, key: str, column_id: Optional[int] = None,
        row_id: Optional[int] = None
    ) -> bool:
        """Test if an annotation with the given key exists for the identified
        object.

        Parameters
        ----------
        key: string
            Unique annotation key.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).

        Returns
        -------
        bool
        """
        raise NotImplementedError()

    @abstractmethod
    def list_annotations(
        self, column_id: Optional[int] = None, row_id: Optional[int] = None
    ) -> Dict:
        """Get all annotations for an identified object as a key,value-pair
        dictionary.

        Parameters
        ----------
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).
        """
        raise NotImplementedError()

    @abstractmethod
    def set_annotation(
        self, key: str, value: Any, column_id: Optional[int] = None,
        row_id: Optional[int] = None
    ):
        """Set annotation value for an identified object.

        Parameters
        ----------
        key: string
            Unique annotation key.
        value: any
            Value that will be associated with the given key.
        column_id: int, default=None
            Column identifier for the referenced object (None for rows or full
            datasets).
        row_id: int, default=None
            Row identifier for the referenced object (None for columns or full
            datasets).
        """
        raise NotImplementedError()
