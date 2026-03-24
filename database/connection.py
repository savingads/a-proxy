"""
Database connection management module.

This module provides the core database connection functionality
with support for connection pooling and configuration.
"""
import sqlite3
import os
from contextlib import contextmanager

# Default database path - use data directory for persistence
DEFAULT_DB_PATH = os.path.join('data', 'personas.db')


class DatabaseConnection:
    """Manages database connections with context manager support."""

    def __init__(self, db_path=None):
        """
        Initialize database connection manager.

        Args:
            db_path: Path to SQLite database file. Defaults to data/personas.db
        """
        self.db_path = db_path or DEFAULT_DB_PATH

        # Ensure data directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def get_connection(self):
        """
        Create a new database connection.

        Returns:
            sqlite3.Connection with row factory enabled
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            with db.transaction() as cursor:
                cursor.execute("INSERT INTO ...")
                # Auto-commits on success, rolls back on exception
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def connection(self):
        """
        Context manager for database connections.

        Usage:
            with db.connection() as conn:
                cursor = conn.cursor()
                ...
        """
        conn = self.get_connection()
        try:
            yield conn
        finally:
            conn.close()


# Global database instance
_db_instance = None


def get_db(db_path=None):
    """
    Get the global database instance.

    Args:
        db_path: Optional path to database file

    Returns:
        DatabaseConnection instance
    """
    global _db_instance
    if _db_instance is None or (db_path and db_path != _db_instance.db_path):
        _db_instance = DatabaseConnection(db_path)
    return _db_instance


def get_db_connection():
    """
    Get a raw database connection (legacy compatibility).

    Returns:
        sqlite3.Connection
    """
    return get_db().get_connection()
