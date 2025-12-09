"""
User repository module.

Handles all database operations related to users and authentication.
"""
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any

from ..connection import get_db_connection
from . import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user data access."""

    def get(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific user by ID.

        Args:
            id: The user ID

        Returns:
            Dictionary containing user data or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        user = cursor.fetchone()

        conn.close()
        return dict(user) if user else None

    def get_all(self, **filters) -> list:
        """
        Get all users.

        Returns:
            List of dictionaries containing user data
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return users

    def save(self, user_data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new user.

        Args:
            user_data: Dictionary with 'email' and 'password_hash'

        Returns:
            The ID of the created user or None if email already exists
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (user_data['email'], user_data['password_hash'])
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def delete(self, id: int) -> bool:
        """
        Delete a user by ID.

        Args:
            id: The user ID to delete

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email address.

        Args:
            email: The email address to search for

        Returns:
            Dictionary containing user data or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()
        return dict(user) if user else None
