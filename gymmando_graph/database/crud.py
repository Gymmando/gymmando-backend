"""Base CRUD operations for all modules.

This module provides a generic base class for CRUD operations that can be
inherited by module-specific CRUD classes to provide standard database
operations.
"""

from typing import Generic, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseCRUD(Generic[T]):
    """Base CRUD class with create, read, update, delete operations.

    Generic base class that provides standard CRUD operations for any
    Pydantic model. Subclasses should specify the table name and model class
    in their __init__ method.

    Type Parameters
    ---------------
    T : TypeVar
        Type variable bound to BaseModel, representing the Pydantic model
        for database records.

    Attributes
    ----------
    table_name : str
        Name of the database table.
    model_class : Type[T]
        Pydantic model class for type-safe operations.

    Examples
    --------
    >>> class MyCRUD(BaseCRUD[MyModel]):
    ...     def __init__(self):
    ...         super().__init__("my_table", MyModel)
    """

    def __init__(self, table_name: str, model_class: Type[T]):
        """Initialize the base CRUD with table name and model class.

        Parameters
        ----------
        table_name : str
            Name of the database table.
        model_class : Type[T]
            Pydantic model class for type-safe operations.
        """
        self.table_name = table_name
        self.model_class = model_class

    def _get_client(self):
        """Get Supabase client instance (lazy loading).

        Returns
        -------
        Client
            Initialized Supabase client for database operations.
        """
        from gymmando_graph.database import get_supabase_client

        return get_supabase_client()

    def create(self, data: dict) -> Optional[T]:
        """Create a new record in the database.

        Parameters
        ----------
        data : dict
            Dictionary containing field values for the new record.

        Returns
        -------
        Optional[T]
            Created model instance if successful, None if database insert
            returned no data.
        """
        client = self._get_client()
        response = client.table(self.table_name).insert(data).execute()
        return self.model_class(**response.data[0]) if response.data else None

    def read(self, id: str) -> Optional[T]:
        """Read a record by ID from the database.

        Parameters
        ----------
        id : str
            Record ID to retrieve.

        Returns
        -------
        Optional[T]
            Model instance if found, None otherwise.
        """
        client = self._get_client()
        response = client.table(self.table_name).select("*").eq("id", id).execute()
        return self.model_class(**response.data[0]) if response.data else None

    def update(self, id: str, data: dict) -> Optional[T]:
        """Update a record in the database.

        Parameters
        ----------
        id : str
            Record ID to update.
        data : dict
            Dictionary containing fields to update.

        Returns
        -------
        Optional[T]
            Updated model instance if successful, None if record not found.
        """
        client = self._get_client()
        response = client.table(self.table_name).update(data).eq("id", id).execute()
        return self.model_class(**response.data[0]) if response.data else None

    def delete(self, id: str) -> bool:
        """Delete a record from the database.

        Parameters
        ----------
        id : str
            Record ID to delete.

        Returns
        -------
        bool
            True if deletion was successful, False otherwise.
        """
        client = self._get_client()
        response = client.table(self.table_name).delete().eq("id", id).execute()
        return bool(response.data)
