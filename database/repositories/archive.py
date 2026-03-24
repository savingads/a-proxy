"""
Archive repository module.

Handles all database operations related to archived websites and mementos.
"""
import json
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..connection import get_db_connection
from . import BaseRepository


class ArchiveRepository(BaseRepository):
    """Repository for archived websites and mementos data access."""

    def get(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific archived website by ID.

        Args:
            id: The archived website ID

        Returns:
            Dictionary containing archived website data or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT aw.* FROM archived_websites aw WHERE aw.id = ?", (id,))
        archived_website = cursor.fetchone()

        if not archived_website:
            conn.close()
            return None

        result = dict(archived_website)
        result['persona_name'] = None if result['persona_id'] is None else f"Persona #{result['persona_id']}"

        conn.close()
        return result

    def get_all(self, **filters) -> List[Dict[str, Any]]:
        """
        Get all archived websites.

        Returns:
            List of dictionaries containing archived website data
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT aw.*
            FROM archived_websites aw
            ORDER BY aw.created_at DESC
        """)

        archived_websites = [dict(row) for row in cursor.fetchall()]

        for website in archived_websites:
            website['persona_name'] = None if website['persona_id'] is None else f"Persona #{website['persona_id']}"

        conn.close()
        return archived_websites

    def save(self, url: str, persona_id: int = None, archive_type: str = 'filesystem',
             archive_location: str = None) -> int:
        """
        Save an archived website to the database.

        Args:
            url: The URL of the website (URI-R)
            persona_id: The ID of the persona used to visit the website
            archive_type: The type of archive (filesystem, postgres, internet_archive)
            archive_location: The path or identifier for the archive

        Returns:
            The ID of the newly created archived website
        """
        if not archive_location:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            archive_location = f"archives/{url_hash}"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO archived_websites
                (uri_r, persona_id, archive_type, archive_location, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (url, persona_id, archive_type, archive_location, datetime.now())
            )

            archived_website_id = cursor.lastrowid
            conn.commit()
            return archived_website_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete(self, id: int) -> bool:
        """
        Delete an archived website and all its associated mementos.

        Args:
            id: The archived website ID to delete

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM archived_websites WHERE id = ?", (id,))
            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # Memento operations

    def save_memento(self, archived_website_id: int, memento_location: str,
                     http_status: int = None, content_type: str = None,
                     content_length: int = None, headers: Dict = None,
                     screenshot_path: str = None, internet_archive_id: str = None) -> int:
        """
        Save a memento for an archived website.

        Args:
            archived_website_id: The ID of the archived website
            memento_location: The path or identifier for this specific memento
            http_status: The HTTP status code of the response
            content_type: The Content-Type of the response
            content_length: The size of the archived content
            headers: Response headers
            screenshot_path: Path to the screenshot
            internet_archive_id: ID/URL if submitted to Internet Archive

        Returns:
            The ID of the newly created memento
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO mementos
                (archived_website_id, memento_datetime, memento_location, http_status,
                 content_type, content_length, headers, screenshot_path, internet_archive_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    archived_website_id,
                    datetime.now(),
                    memento_location,
                    http_status,
                    content_type,
                    content_length,
                    json.dumps(headers) if headers else None,
                    screenshot_path,
                    internet_archive_id,
                    datetime.now()
                )
            )

            memento_id = cursor.lastrowid
            conn.commit()
            return memento_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_mementos(self, archived_website_id: int) -> List[Dict[str, Any]]:
        """
        Get all mementos for a specific archived website.

        Args:
            archived_website_id: The ID of the archived website

        Returns:
            List of dictionaries containing memento data
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM mementos
            WHERE archived_website_id = ?
            ORDER BY memento_datetime DESC
        """, (archived_website_id,))

        mementos = [dict(row) for row in cursor.fetchall()]

        for memento in mementos:
            if memento['headers']:
                memento['headers'] = json.loads(memento['headers'])

        conn.close()
        return mementos

    def get_memento(self, memento_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific memento.

        Args:
            memento_id: The ID of the memento

        Returns:
            Dictionary containing memento data or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT m.*, aw.uri_r
            FROM mementos m
            JOIN archived_websites aw ON m.archived_website_id = aw.id
            WHERE m.id = ?
        """, (memento_id,))

        memento = cursor.fetchone()
        if not memento:
            conn.close()
            return None

        result = dict(memento)
        if result['headers']:
            result['headers'] = json.loads(result['headers'])

        conn.close()
        return result
