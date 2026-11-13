# backend/app/database.py
import os
import sqlite3

from ..config import DATABASE_URL

# Parse the SQLite file path from the DATABASE_URL (format: sqlite:///./path/to/db)
_db_path = DATABASE_URL.replace('sqlite:///', '', 1)
_db_path = os.path.abspath(_db_path)

def init_db():
    """Create the users table if it doesn't exist."""
    conn = sqlite3.connect(_db_path, check_same_thread=False)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Ensure the DB and table are ready at import time
init_db()

def get_db():
    """Dependency that yields a SQLite connection.
    The caller is responsible for closing it (FastAPI will do it automatically).
    """
    conn = sqlite3.connect(_db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

