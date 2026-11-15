# backend/app/database.py
"""
FoodFresh AI - SQLite Database Compatibility Module
Connects seamlessly to the production FoodFresh AI database.
"""
import os
import sqlite3
from typing import Generator

from backend.app.database.chat_db import DB_PATH, get_db_connection

# Base is also exposed here in case models or router imports Base from database
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
