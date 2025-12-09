"""
Persona repository module.

Handles all database operations related to personas and their associated data.
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..connection import get_db_connection
from ..models import Persona, DemographicData, PsychographicData, BehavioralData, ContextualData
from . import BaseRepository


class PersonaRepository(BaseRepository):
    """Repository for persona data access."""

    def get(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific persona by ID.

        Args:
            id: The persona ID

        Returns:
            Dictionary containing persona data or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM personas WHERE id = ?", (id,))
        persona_row = cursor.fetchone()

        if not persona_row:
            conn.close()
            return None

        persona = dict(persona_row)
        persona.update(self._get_persona_data(cursor, id))

        conn.close()
        return persona

    def get_all(self, page: int = 1, per_page: int = 100, **filters) -> Dict[str, Any]:
        """
        Get all personas with pagination.

        Args:
            page: Page number (1-indexed)
            per_page: Number of personas per page
            **filters: Additional filters (not implemented yet)

        Returns:
            Dictionary with 'personas' list and pagination info
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        offset = (page - 1) * per_page

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM personas")
        total = cursor.fetchone()[0]

        # Get personas for this page
        cursor.execute("""
            SELECT p.* FROM personas p
            ORDER BY p.updated_at DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))

        personas = []
        for row in cursor.fetchall():
            persona = dict(row)
            persona.update(self._get_persona_data(cursor, persona['id']))
            personas.append(persona)

        conn.close()

        return {
            'personas': personas,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

    def save(self, persona_data: Dict[str, Any]) -> int:
        """
        Save a persona to the database.

        Args:
            persona_data: Dictionary containing persona information

        Returns:
            The ID of the saved persona
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            persona_id = persona_data.get('id')
            now = datetime.now()

            if persona_id:
                # Update existing persona
                cursor.execute(
                    "UPDATE personas SET name = ?, updated_at = ? WHERE id = ?",
                    (persona_data.get('name', 'Unnamed Persona'), now, persona_id)
                )
            else:
                # Create new persona
                cursor.execute(
                    "INSERT INTO personas (name, created_at, updated_at) VALUES (?, ?, ?)",
                    (persona_data.get('name', 'Unnamed Persona'), now, now)
                )
                persona_id = cursor.lastrowid

            # Save associated data
            if 'demographic' in persona_data:
                self._save_demographic_data(cursor, persona_id, persona_data['demographic'])

            if 'psychographic' in persona_data:
                self._save_psychographic_data(cursor, persona_id, persona_data['psychographic'])

            if 'behavioral' in persona_data:
                self._save_behavioral_data(cursor, persona_id, persona_data['behavioral'])

            if 'contextual' in persona_data:
                self._save_contextual_data(cursor, persona_id, persona_data['contextual'])

            conn.commit()
            return persona_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete(self, id: int) -> bool:
        """
        Delete a persona and all associated data.

        Args:
            id: The persona ID to delete

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Delete the persona (CASCADE will delete related data)
            cursor.execute("DELETE FROM personas WHERE id = ?", (id,))

            # Explicitly delete related data to ensure cleanup
            cursor.execute("DELETE FROM demographic_data WHERE persona_id = ?", (id,))
            cursor.execute("DELETE FROM psychographic_data WHERE persona_id = ?", (id,))
            cursor.execute("DELETE FROM behavioral_data WHERE persona_id = ?", (id,))
            cursor.execute("DELETE FROM contextual_data WHERE persona_id = ?", (id,))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _get_persona_data(self, cursor, persona_id: int) -> Dict[str, Any]:
        """Helper function to get all persona data for a given persona ID."""
        data = {
            'demographic': {},
            'psychographic': {},
            'behavioral': {},
            'contextual': {}
        }

        # Get demographic data
        cursor.execute("SELECT * FROM demographic_data WHERE persona_id = ?", (persona_id,))
        demo_row = cursor.fetchone()
        if demo_row:
            demo_data = dict(demo_row)
            if demo_data.get('latitude') and demo_data.get('longitude'):
                demo_data['geolocation'] = f"{demo_data['latitude']},{demo_data['longitude']}"
            data['demographic'] = demo_data

        # Get psychographic data
        cursor.execute("SELECT * FROM psychographic_data WHERE persona_id = ?", (persona_id,))
        psycho_row = cursor.fetchone()
        if psycho_row:
            psycho_data = dict(psycho_row)
            for field in ['interests', 'personal_values', 'attitudes', 'opinions']:
                if psycho_data.get(field):
                    try:
                        psycho_data[field] = json.loads(psycho_data[field])
                    except:
                        psycho_data[field] = []
            data['psychographic'] = psycho_data

        # Get behavioral data
        cursor.execute("SELECT * FROM behavioral_data WHERE persona_id = ?", (persona_id,))
        behav_row = cursor.fetchone()
        if behav_row:
            behav_data = dict(behav_row)
            for field in ['browsing_habits', 'purchase_history', 'brand_interactions']:
                if behav_data.get(field):
                    try:
                        behav_data[field] = json.loads(behav_data[field])
                    except:
                        behav_data[field] = []
            for field in ['device_usage', 'social_media_activity', 'content_consumption']:
                if behav_data.get(field):
                    try:
                        behav_data[field] = json.loads(behav_data[field])
                    except:
                        behav_data[field] = {}
            data['behavioral'] = behav_data

        # Get contextual data
        cursor.execute("SELECT * FROM contextual_data WHERE persona_id = ?", (persona_id,))
        context_row = cursor.fetchone()
        if context_row:
            data['contextual'] = dict(context_row)

        return data

    def _save_demographic_data(self, cursor, persona_id: int, demo_data: Dict[str, Any]):
        """Save demographic data for a persona."""
        latitude = None
        longitude = None
        geolocation = demo_data.get('geolocation', '')
        if geolocation and ',' in geolocation:
            try:
                lat_str, lng_str = geolocation.split(',', 1)
                latitude = float(lat_str.strip())
                longitude = float(lng_str.strip())
            except (ValueError, TypeError):
                pass

        cursor.execute("SELECT id FROM demographic_data WHERE persona_id = ?", (persona_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute("""
                UPDATE demographic_data SET
                latitude = ?, longitude = ?, language = ?, country = ?, city = ?, region = ?,
                age = ?, gender = ?, education = ?, income = ?, occupation = ?
                WHERE persona_id = ?
            """, (
                latitude, longitude, demo_data.get('language'), demo_data.get('country'),
                demo_data.get('city'), demo_data.get('region'), demo_data.get('age'),
                demo_data.get('gender'), demo_data.get('education'), demo_data.get('income'),
                demo_data.get('occupation'), persona_id
            ))
        else:
            cursor.execute("""
                INSERT INTO demographic_data
                (persona_id, latitude, longitude, language, country, city, region, age, gender, education, income, occupation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                persona_id, latitude, longitude, demo_data.get('language'), demo_data.get('country'),
                demo_data.get('city'), demo_data.get('region'), demo_data.get('age'),
                demo_data.get('gender'), demo_data.get('education'), demo_data.get('income'),
                demo_data.get('occupation')
            ))

    def _save_psychographic_data(self, cursor, persona_id: int, psycho_data: Dict[str, Any]):
        """Save psychographic data for a persona."""
        cursor.execute("SELECT id FROM psychographic_data WHERE persona_id = ?", (persona_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute("""
                UPDATE psychographic_data SET
                interests = ?, personal_values = ?, attitudes = ?, lifestyle = ?, personality = ?, opinions = ?
                WHERE persona_id = ?
            """, (
                json.dumps(psycho_data.get('interests', [])),
                json.dumps(psycho_data.get('personal_values', [])),
                json.dumps(psycho_data.get('attitudes', [])),
                psycho_data.get('lifestyle'),
                psycho_data.get('personality'),
                json.dumps(psycho_data.get('opinions', [])),
                persona_id
            ))
        else:
            cursor.execute("""
                INSERT INTO psychographic_data
                (persona_id, interests, personal_values, attitudes, lifestyle, personality, opinions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                persona_id,
                json.dumps(psycho_data.get('interests', [])),
                json.dumps(psycho_data.get('personal_values', [])),
                json.dumps(psycho_data.get('attitudes', [])),
                psycho_data.get('lifestyle'),
                psycho_data.get('personality'),
                json.dumps(psycho_data.get('opinions', []))
            ))

    def _save_behavioral_data(self, cursor, persona_id: int, behav_data: Dict[str, Any]):
        """Save behavioral data for a persona."""
        cursor.execute("SELECT id FROM behavioral_data WHERE persona_id = ?", (persona_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute("""
                UPDATE behavioral_data SET
                browsing_habits = ?, purchase_history = ?, brand_interactions = ?,
                device_usage = ?, social_media_activity = ?, content_consumption = ?
                WHERE persona_id = ?
            """, (
                json.dumps(behav_data.get('browsing_habits', [])),
                json.dumps(behav_data.get('purchase_history', [])),
                json.dumps(behav_data.get('brand_interactions', [])),
                json.dumps(behav_data.get('device_usage', {})),
                json.dumps(behav_data.get('social_media_activity', {})),
                json.dumps(behav_data.get('content_consumption', {})),
                persona_id
            ))
        else:
            cursor.execute("""
                INSERT INTO behavioral_data
                (persona_id, browsing_habits, purchase_history, brand_interactions, device_usage, social_media_activity, content_consumption)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                persona_id,
                json.dumps(behav_data.get('browsing_habits', [])),
                json.dumps(behav_data.get('purchase_history', [])),
                json.dumps(behav_data.get('brand_interactions', [])),
                json.dumps(behav_data.get('device_usage', {})),
                json.dumps(behav_data.get('social_media_activity', {})),
                json.dumps(behav_data.get('content_consumption', {}))
            ))

    def _save_contextual_data(self, cursor, persona_id: int, context_data: Dict[str, Any]):
        """Save contextual data for a persona."""
        cursor.execute("SELECT id FROM contextual_data WHERE persona_id = ?", (persona_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute("""
                UPDATE contextual_data SET
                time_of_day = ?, day_of_week = ?, season = ?, weather = ?,
                device_type = ?, browser_type = ?, screen_size = ?, connection_type = ?
                WHERE persona_id = ?
            """, (
                context_data.get('time_of_day'), context_data.get('day_of_week'),
                context_data.get('season'), context_data.get('weather'),
                context_data.get('device_type'), context_data.get('browser_type'),
                context_data.get('screen_size'), context_data.get('connection_type'),
                persona_id
            ))
        else:
            cursor.execute("""
                INSERT INTO contextual_data
                (persona_id, time_of_day, day_of_week, season, weather, device_type, browser_type, screen_size, connection_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                persona_id,
                context_data.get('time_of_day'), context_data.get('day_of_week'),
                context_data.get('season'), context_data.get('weather'),
                context_data.get('device_type'), context_data.get('browser_type'),
                context_data.get('screen_size'), context_data.get('connection_type')
            ))
