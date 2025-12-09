"""
Database package for A-Proxy.

This package provides database access through a repository pattern while
maintaining backward compatibility with the legacy function-based API.

Usage:
    # New repository pattern (recommended)
    from database.repositories import PersonaRepository
    repo = PersonaRepository()
    persona = repo.get(1)

    # Legacy function API (backward compatible)
    from database import get_persona, save_persona
    persona = get_persona(1)
"""
from datetime import datetime

from .connection import get_db_connection, get_db, DatabaseConnection

# Import repositories
from .repositories.persona import PersonaRepository
from .repositories.journey import JourneyRepository
from .repositories.archive import ArchiveRepository
from .repositories.user import UserRepository
from .repositories.settings import SettingsRepository

# Initialize repository singletons
_persona_repo = None
_journey_repo = None
_archive_repo = None
_user_repo = None
_settings_repo = None


def _get_persona_repo():
    global _persona_repo
    if _persona_repo is None:
        _persona_repo = PersonaRepository()
    return _persona_repo


def _get_journey_repo():
    global _journey_repo
    if _journey_repo is None:
        _journey_repo = JourneyRepository()
    return _journey_repo


def _get_archive_repo():
    global _archive_repo
    if _archive_repo is None:
        _archive_repo = ArchiveRepository()
    return _archive_repo


def _get_user_repo():
    global _user_repo
    if _user_repo is None:
        _user_repo = UserRepository()
    return _user_repo


def _get_settings_repo():
    global _settings_repo
    if _settings_repo is None:
        _settings_repo = SettingsRepository()
    return _settings_repo


# ============================================================================
# Schema Initialization
# ============================================================================

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create archived websites table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS archived_websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uri_r TEXT NOT NULL,
        persona_id INTEGER,
        archive_type TEXT NOT NULL,
        archive_location TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create mementos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mementos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        archived_website_id INTEGER NOT NULL,
        memento_datetime TIMESTAMP NOT NULL,
        memento_location TEXT NOT NULL,
        http_status INTEGER,
        content_type TEXT,
        content_length INTEGER,
        headers TEXT,
        screenshot_path TEXT,
        internet_archive_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (archived_website_id) REFERENCES archived_websites (id) ON DELETE CASCADE
    )
    ''')

    # Create journeys table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS journeys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        persona_id INTEGER,
        journey_type TEXT DEFAULT 'marketing',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create waypoints table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS waypoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journey_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        title TEXT,
        notes TEXT,
        screenshot_path TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sequence_number INTEGER,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        type TEXT DEFAULT 'browse',
        agent_data TEXT,
        FOREIGN KEY (journey_id) REFERENCES journeys (id) ON DELETE CASCADE
    )
    ''')

    # Check if type column exists in waypoints table
    cursor.execute("PRAGMA table_info(waypoints)")
    columns = cursor.fetchall()
    column_names = [col['name'] for col in columns]

    if 'type' not in column_names:
        cursor.execute("ALTER TABLE waypoints ADD COLUMN type TEXT DEFAULT 'browse'")

    if 'agent_data' not in column_names:
        cursor.execute("ALTER TABLE waypoints ADD COLUMN agent_data TEXT")

    conn.commit()
    conn.close()


def create_persona_tables():
    """Create persona-related tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS demographic_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona_id INTEGER NOT NULL,
        latitude REAL,
        longitude REAL,
        language TEXT,
        country TEXT,
        city TEXT,
        region TEXT,
        age INTEGER,
        gender TEXT,
        education TEXT,
        income TEXT,
        occupation TEXT,
        FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS psychographic_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona_id INTEGER NOT NULL,
        interests TEXT,
        personal_values TEXT,
        attitudes TEXT,
        lifestyle TEXT,
        personality TEXT,
        opinions TEXT,
        FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS behavioral_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona_id INTEGER NOT NULL,
        browsing_habits TEXT,
        purchase_history TEXT,
        brand_interactions TEXT,
        device_usage TEXT,
        social_media_activity TEXT,
        content_consumption TEXT,
        FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contextual_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona_id INTEGER NOT NULL,
        time_of_day TEXT,
        day_of_week TEXT,
        season TEXT,
        weather TEXT,
        device_type TEXT,
        browser_type TEXT,
        screen_size TEXT,
        connection_type TEXT,
        FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()


def init_settings_table():
    """Initialize the settings table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        description TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()


def init_user_table():
    """Initialize the users table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()


def init_default_settings():
    """Initialize default settings if they don't exist."""
    repo = _get_settings_repo()
    repo.save('internet_archive_enabled', 'true', 'Enable Internet Archive integration')
    repo.save('internet_archive_rate_limit', '10', 'Maximum Internet Archive submissions per day')
    repo.save('internet_archive_submissions_today', '0', 'Number of Internet Archive submissions made today')
    repo.save('internet_archive_last_reset', datetime.now().strftime('%Y-%m-%d'),
              'Last date the submission counter was reset')


def initialize_database():
    """Initialize all database tables. Call this on application startup."""
    init_db()
    create_persona_tables()
    init_settings_table()
    init_user_table()
    init_default_settings()


# ============================================================================
# Legacy API - Backward Compatible Functions
# ============================================================================

# --- Archive functions ---
def save_archived_website(url, persona_id=None, archive_type='filesystem', archive_location=None):
    return _get_archive_repo().save(url, persona_id, archive_type, archive_location)


def save_memento(archived_website_id, memento_location, http_status=None,
                 content_type=None, content_length=None, headers=None,
                 screenshot_path=None, internet_archive_id=None):
    return _get_archive_repo().save_memento(
        archived_website_id, memento_location, http_status,
        content_type, content_length, headers, screenshot_path, internet_archive_id
    )


def get_archived_website(archived_website_id):
    return _get_archive_repo().get(archived_website_id)


def get_all_archived_websites():
    return _get_archive_repo().get_all()


def get_mementos_for_website(archived_website_id):
    return _get_archive_repo().get_mementos(archived_website_id)


def get_memento(memento_id):
    return _get_archive_repo().get_memento(memento_id)


def delete_archived_website(archived_website_id):
    return _get_archive_repo().delete(archived_website_id)


# --- Journey functions ---
def create_journey(name, description=None, persona_id=None, journey_type='marketing', status='active'):
    return _get_journey_repo().save({
        'name': name,
        'description': description,
        'persona_id': persona_id,
        'journey_type': journey_type,
        'status': status
    })


def get_journey(journey_id):
    return _get_journey_repo().get(journey_id)


def get_all_journeys():
    return _get_journey_repo().get_all()


def update_journey(journey_id, name=None, description=None, persona_id=None, journey_type=None, status=None):
    updates = {'id': journey_id}
    if name is not None:
        updates['name'] = name
    if description is not None:
        updates['description'] = description
    if persona_id is not None:
        updates['persona_id'] = persona_id
    if journey_type is not None:
        updates['journey_type'] = journey_type
    if status is not None:
        updates['status'] = status
    return _get_journey_repo().save(updates)


def delete_journey(journey_id):
    return _get_journey_repo().delete(journey_id)


def add_waypoint(journey_id, url, title=None, notes=None, screenshot_path=None,
                 metadata=None, type='browse', agent_data=None):
    return _get_journey_repo().add_waypoint(
        journey_id, url, title, notes, screenshot_path, metadata, type, agent_data
    )


def get_waypoints(journey_id):
    return _get_journey_repo().get_waypoints(journey_id)


def get_waypoint(waypoint_id):
    return _get_journey_repo().get_waypoint(waypoint_id)


def update_waypoint(waypoint_id, title=None, notes=None, sequence_number=None, type=None, agent_data=None):
    return _get_journey_repo().update_waypoint(
        waypoint_id, title=title, notes=notes, sequence_number=sequence_number,
        type=type, agent_data=agent_data
    )


def delete_waypoint(waypoint_id):
    return _get_journey_repo().delete_waypoint(waypoint_id)


# --- Persona functions ---
def get_all_personas(page=1, per_page=100):
    return _get_persona_repo().get_all(page, per_page)


def get_persona(persona_id):
    return _get_persona_repo().get(persona_id)


def save_persona(persona_data):
    return _get_persona_repo().save(persona_data)


def delete_persona(persona_id):
    return _get_persona_repo().delete(persona_id)


# --- Settings functions ---
def get_setting(key, default=None):
    return _get_settings_repo().get_with_default(key, default)


def set_setting(key, value, description=None):
    return _get_settings_repo().save(key, value, description)


def get_all_settings():
    return _get_settings_repo().get_all()


# --- User functions ---
def create_user(email, password_hash):
    return _get_user_repo().save({'email': email, 'password_hash': password_hash})


def get_user_by_email(email):
    return _get_user_repo().get_by_email(email)


# ============================================================================
# Auto-initialize on import (for backward compatibility)
# ============================================================================
initialize_database()
