"""
User repository module.

Handles all database operations related to users and authentication.
"""
import sqlite3
from typing import Optional, Dict, Any

from ..connection import get_db
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
        with get_db().cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
            user = cursor.fetchone()
        return dict(user) if user else None

    def get_all(self, **filters) -> list:
        """
        Get all users. (Required by the BaseRepository ABC interface.)

        Returns:
            List of dictionaries containing user data
        """
        with get_db().cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            users = [dict(row) for row in cursor.fetchall()]
        return users

    def save(self, user_data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new user.

        Args:
            user_data: Dictionary with 'email' and 'password_hash'

        Returns:
            The ID of the created user or None if email already exists
        """
        try:
            with get_db().transaction() as cursor:
                cursor.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (user_data['email'], user_data['password_hash'])
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def delete(self, id: int) -> bool:
        """
        Delete a user by ID.

        Args:
            id: The user ID to delete

        Returns:
            True if successful
        """
        with get_db().transaction() as cursor:
            cursor.execute("DELETE FROM users WHERE id = ?", (id,))
        return True

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email address.

        Args:
            email: The email address to search for

        Returns:
            Dictionary containing user data or None if not found
        """
        with get_db().cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
        return dict(user) if user else None
