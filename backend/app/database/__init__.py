# backend/app/database/__init__.py
"""
FoodFresh AI - Database Package
Exposes both the core SQLite chat_db connection and get_db dependency.
"""
import sqlite3
from typing import Generator
from .chat_db import DB_PATH, get_db_connection

try:
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
except ImportError:
    Base = object

def init_db() -> None:
    """Ensure database connection and schema initialization."""
    conn = get_db_connection()
    conn.close()

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Dependency that yields a SQLite connection to the FoodFresh AI database."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

__all__ = ["get_db_connection", "get_db", "init_db", "DB_PATH", "Base"]
