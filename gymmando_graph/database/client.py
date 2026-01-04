"""Supabase database client initialization module.

This module provides a singleton Supabase client instance with lazy loading
for database operations across the application.
"""

import os

from dotenv import load_dotenv
from supabase import Client, create_client

from gymmando_graph.utils import Logger

logger = Logger().get_logger()

load_dotenv()


_client: Client = None


def get_supabase_client() -> Client:
    """Get initialized Supabase client instance (lazy loading).

    Returns a singleton Supabase client instance. The client is created on
    first call and reused for subsequent calls. Environment variables
    SUPABASE_URL and SUPABASE_KEY must be set.

    Returns
    -------
    Client
        Initialized Supabase client instance.

    Raises
    ------
    ValueError
        If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
    Exception
        If Supabase client creation fails for any reason.

    Notes
    -----
    Uses lazy loading pattern - the client is only created when first accessed,
    not at module import time. This allows the module to be imported even if
    environment variables are not yet set.
    """
    global _client
    if _client is not None:
        return _client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

    try:
        _client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
        return _client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise


# supabase: Client = get_supabase_client()
