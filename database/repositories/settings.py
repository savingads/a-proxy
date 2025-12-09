"""
Settings repository module.

Handles all database operations related to application settings.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..connection import get_db_connection
from . import BaseRepository


class SettingsRepository(BaseRepository):
    """Repository for application settings data access."""

    def get(self, key: str) -> Optional[str]:
        """
        Get a setting value by key.

        Args:
            key: The setting key

        Returns:
            The setting value or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()

        conn.close()
        return result['value'] if result else None

    def get_with_default(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value by key with a default fallback.

        Args:
            key: The setting key
            default: Default value if setting doesn't exist

        Returns:
            The setting value or default if not found
        """
        value = self.get(key)
        return value if value is not None else default

    def get_all(self, **filters) -> List[Dict[str, Any]]:
        """
        Get all settings.

        Returns:
            List of dictionaries containing setting data
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM settings ORDER BY key")
        settings = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return settings

    def save(self, key: str, value: str, description: str = None) -> bool:
        """
        Set a setting value.

        Args:
            key: The setting key
            value: The setting value
            description: Optional description of the setting

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT key FROM settings WHERE key = ?", (key,))
            exists = cursor.fetchone()

            if exists:
                cursor.execute(
                    "UPDATE settings SET value = ?, updated_at = ? WHERE key = ?",
                    (value, datetime.now(), key)
                )
            else:
                cursor.execute(
                    "INSERT INTO settings (key, value, description, updated_at) VALUES (?, ?, ?, ?)",
                    (key, value, description, datetime.now())
                )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete(self, key: str) -> bool:
        """
        Delete a setting by key.

        Args:
            key: The setting key to delete

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
