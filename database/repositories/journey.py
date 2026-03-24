"""
Journey repository module.

Handles all database operations related to journeys and waypoints.
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..connection import get_db_connection
from . import BaseRepository


class JourneyRepository(BaseRepository):
    """Repository for journey and waypoint data access."""

    def get(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific journey by ID.

        Args:
            id: The journey ID

        Returns:
            Dictionary containing journey data or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT j.* FROM journeys j WHERE j.id = ?", (id,))
        journey = cursor.fetchone()

        if not journey:
            conn.close()
            return None

        result = dict(journey)
        # Add placeholder for persona_name for compatibility
        result['persona_name'] = None if result['persona_id'] is None else f"Persona #{result['persona_id']}"

        conn.close()
        return result

    def get_all(self, **filters) -> List[Dict[str, Any]]:
        """
        Get all journeys.

        Returns:
            List of dictionaries containing journey data
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.*
            FROM journeys j
            ORDER BY j.updated_at DESC
        """)

        journeys = [dict(row) for row in cursor.fetchall()]

        for journey in journeys:
            journey['persona_name'] = None if journey['persona_id'] is None else f"Persona #{journey['persona_id']}"

        conn.close()
        return journeys

    def save(self, journey_data: Dict[str, Any]) -> int:
        """
        Create or update a journey.

        Args:
            journey_data: Dictionary containing journey information

        Returns:
            The ID of the saved journey
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            journey_id = journey_data.get('id')
            now = datetime.now()

            if journey_id:
                # Build update query dynamically
                updates = {}
                for key in ['name', 'description', 'persona_id', 'journey_type', 'status']:
                    if key in journey_data:
                        updates[key] = journey_data[key]

                if updates:
                    updates['updated_at'] = now
                    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                    query = f"UPDATE journeys SET {set_clause} WHERE id = ?"
                    params = list(updates.values()) + [journey_id]
                    cursor.execute(query, params)
            else:
                # Create new journey
                cursor.execute(
                    """
                    INSERT INTO journeys
                    (name, description, persona_id, journey_type, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        journey_data.get('name', ''),
                        journey_data.get('description'),
                        journey_data.get('persona_id'),
                        journey_data.get('journey_type', 'marketing'),
                        journey_data.get('status', 'active'),
                        now,
                        now
                    )
                )
                journey_id = cursor.lastrowid

            conn.commit()
            return journey_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete(self, id: int) -> bool:
        """
        Delete a journey and all its associated waypoints.

        Args:
            id: The journey ID to delete

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Delete the journey (CASCADE will delete related waypoints)
            cursor.execute("DELETE FROM journeys WHERE id = ?", (id,))
            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # Waypoint operations

    def add_waypoint(self, journey_id: int, url: str, title: str = None,
                     notes: str = None, screenshot_path: str = None,
                     metadata: Dict = None, waypoint_type: str = 'browse',
                     agent_data: str = None) -> int:
        """
        Add a waypoint to a journey.

        Args:
            journey_id: The ID of the journey
            url: The URL of the waypoint
            title: The title of the page/waypoint
            notes: Any notes about this waypoint
            screenshot_path: Path to a screenshot
            metadata: Additional metadata
            waypoint_type: Type of waypoint ('browse' or 'agent')
            agent_data: JSON string of agent conversation data

        Returns:
            The ID of the newly created waypoint
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Get sequence number
            cursor.execute(
                "SELECT COUNT(*) as count FROM waypoints WHERE journey_id = ?",
                (journey_id,)
            )
            count = cursor.fetchone()['count']
            sequence_number = count + 1

            cursor.execute(
                """
                INSERT INTO waypoints
                (journey_id, url, title, notes, screenshot_path, timestamp,
                 sequence_number, metadata, created_at, type, agent_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    journey_id,
                    url,
                    title,
                    notes,
                    screenshot_path,
                    datetime.now(),
                    sequence_number,
                    json.dumps(metadata) if metadata else None,
                    datetime.now(),
                    waypoint_type,
                    agent_data
                )
            )

            waypoint_id = cursor.lastrowid

            # Update journey's updated_at timestamp
            cursor.execute(
                "UPDATE journeys SET updated_at = ? WHERE id = ?",
                (datetime.now(), journey_id)
            )

            conn.commit()
            return waypoint_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_waypoints(self, journey_id: int) -> List[Dict[str, Any]]:
        """
        Get all waypoints for a journey.

        Args:
            journey_id: The ID of the journey

        Returns:
            List of dictionaries containing waypoint data
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM waypoints
            WHERE journey_id = ?
            ORDER BY sequence_number ASC
        """, (journey_id,))

        waypoints = [dict(row) for row in cursor.fetchall()]

        for waypoint in waypoints:
            if waypoint['metadata']:
                waypoint['metadata'] = json.loads(waypoint['metadata'])
            if waypoint['timestamp'] and isinstance(waypoint['timestamp'], str):
                try:
                    waypoint['timestamp'] = datetime.fromisoformat(
                        waypoint['timestamp'].replace('Z', '+00:00')
                    )
                except ValueError:
                    pass

        conn.close()
        return waypoints

    def get_waypoint(self, waypoint_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific waypoint.

        Args:
            waypoint_id: The ID of the waypoint

        Returns:
            Dictionary containing waypoint data or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT w.*, j.name as journey_name
            FROM waypoints w
            JOIN journeys j ON w.journey_id = j.id
            WHERE w.id = ?
        """, (waypoint_id,))

        waypoint = cursor.fetchone()
        if not waypoint:
            conn.close()
            return None

        result = dict(waypoint)
        if result['metadata']:
            result['metadata'] = json.loads(result['metadata'])

        conn.close()
        return result

    def update_waypoint(self, waypoint_id: int, **updates) -> bool:
        """
        Update a waypoint.

        Args:
            waypoint_id: The ID of the waypoint to update
            **updates: Fields to update (title, notes, sequence_number, type, agent_data)

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            allowed_fields = ['title', 'notes', 'sequence_number', 'type', 'agent_data']
            update_data = {k: v for k, v in updates.items() if k in allowed_fields and v is not None}

            if not update_data:
                return True

            set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
            query = f"UPDATE waypoints SET {set_clause} WHERE id = ?"
            params = list(update_data.values()) + [waypoint_id]

            cursor.execute(query, params)

            # Update journey timestamp
            cursor.execute(
                """
                UPDATE journeys
                SET updated_at = ?
                WHERE id = (SELECT journey_id FROM waypoints WHERE id = ?)
                """,
                (datetime.now(), waypoint_id)
            )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_waypoint(self, waypoint_id: int) -> bool:
        """
        Delete a waypoint.

        Args:
            waypoint_id: The ID of the waypoint to delete

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Get journey_id before deleting
            cursor.execute(
                "SELECT journey_id FROM waypoints WHERE id = ?",
                (waypoint_id,)
            )
            waypoint = cursor.fetchone()
            if not waypoint:
                conn.close()
                return False

            journey_id = waypoint['journey_id']

            # Delete the waypoint
            cursor.execute("DELETE FROM waypoints WHERE id = ?", (waypoint_id,))

            # Update journey timestamp
            cursor.execute(
                "UPDATE journeys SET updated_at = ? WHERE id = ?",
                (datetime.now(), journey_id)
            )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
