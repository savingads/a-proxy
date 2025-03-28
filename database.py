import sqlite3
import os
import json
from datetime import datetime

# Define the database path - use a simple path in the current directory
DB_PATH = 'personas.db'

# No need to create a directory for a file in the current directory

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create personas table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Update demographic_data table to include latitude and longitude
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
    
    # Create psychographic data table
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
    
    # Create behavioral data table
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
    
    # Create contextual data table
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
    
    # Create archived websites table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS archived_websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uri_r TEXT NOT NULL,
        persona_id INTEGER,
        archive_type TEXT NOT NULL,
        archive_location TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE SET NULL
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
    
    conn.commit()
    conn.close()

def save_persona(persona_data):
    """
    Save a persona and its associated data to the database
    
    Args:
        persona_data: Dictionary containing persona information with keys:
            - name: Name of the persona
            - demographic: Dictionary of demographic data
            - psychographic: Dictionary of psychographic data
            - behavioral: Dictionary of behavioral data
            - contextual: Dictionary of contextual data
    
    Returns:
        The ID of the newly created persona
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert persona record
        cursor.execute(
            "INSERT INTO personas (name, created_at, updated_at) VALUES (?, ?, ?)",
            (persona_data.get('name', 'Unnamed Persona'), 
             datetime.now(), 
             datetime.now())
        )
        persona_id = cursor.lastrowid
        
        # Insert demographic data
        demographic = persona_data.get('demographic', {})
        cursor.execute(
            """
            INSERT INTO demographic_data 
            (persona_id, latitude, longitude, language, country, city, region, age, gender, education, income, occupation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                persona_id,
                demographic.get('latitude'),
                demographic.get('longitude'),
                demographic.get('language'),
                demographic.get('country'),
                demographic.get('city'),
                demographic.get('region'),
                demographic.get('age'),
                demographic.get('gender'),
                demographic.get('education'),
                demographic.get('income'),
                demographic.get('occupation')
            )
        )
        
        # Insert psychographic data
        psychographic = persona_data.get('psychographic', {})
        cursor.execute(
            """
            INSERT INTO psychographic_data 
            (persona_id, interests, personal_values, attitudes, lifestyle, personality, opinions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                persona_id,
                json.dumps(psychographic.get('interests', [])),
                json.dumps(psychographic.get('personal_values', [])),
                json.dumps(psychographic.get('attitudes', [])),
                psychographic.get('lifestyle'),
                psychographic.get('personality'),
                json.dumps(psychographic.get('opinions', []))
            )
        )
        
        # Insert behavioral data
        behavioral = persona_data.get('behavioral', {})
        cursor.execute(
            """
            INSERT INTO behavioral_data 
            (persona_id, browsing_habits, purchase_history, brand_interactions, 
             device_usage, social_media_activity, content_consumption)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                persona_id,
                json.dumps(behavioral.get('browsing_habits', [])),
                json.dumps(behavioral.get('purchase_history', [])),
                json.dumps(behavioral.get('brand_interactions', [])),
                json.dumps(behavioral.get('device_usage', {})),
                json.dumps(behavioral.get('social_media_activity', {})),
                json.dumps(behavioral.get('content_consumption', {}))
            )
        )
        
        # Insert contextual data
        contextual = persona_data.get('contextual', {})
        cursor.execute(
            """
            INSERT INTO contextual_data 
            (persona_id, time_of_day, day_of_week, season, weather, 
             device_type, browser_type, screen_size, connection_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                persona_id,
                contextual.get('time_of_day'),
                contextual.get('day_of_week'),
                contextual.get('season'),
                contextual.get('weather'),
                contextual.get('device_type'),
                contextual.get('browser_type'),
                contextual.get('screen_size'),
                contextual.get('connection_type')
            )
        )
        
        conn.commit()
        return persona_id
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def get_all_personas():
    """Retrieve all personas from the database with all their associated data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First get all personas basic info
    cursor.execute("""
    SELECT p.id, p.name, p.created_at, p.updated_at,
           d.latitude, d.longitude, d.language, d.country, d.city, d.region
    FROM personas p
    LEFT JOIN demographic_data d ON p.id = d.persona_id
    ORDER BY p.updated_at DESC
    """)
    
    personas = [dict(row) for row in cursor.fetchall()]
    
    # Now for each persona, get their associated data
    for persona in personas:
        persona_id = persona['id']
        
        # Get psychographic data
        cursor.execute("SELECT * FROM psychographic_data WHERE persona_id = ?", (persona_id,))
        psychographic = cursor.fetchone()
        if psychographic:
            persona['psychographic'] = dict(psychographic)
            # Parse JSON fields
            for field in ['interests', 'personal_values', 'attitudes', 'opinions']:
                if persona['psychographic'][field]:
                    persona['psychographic'][field] = json.loads(persona['psychographic'][field])
        
        # Get behavioral data
        cursor.execute("SELECT * FROM behavioral_data WHERE persona_id = ?", (persona_id,))
        behavioral = cursor.fetchone()
        if behavioral:
            persona['behavioral'] = dict(behavioral)
            # Parse JSON fields
            for field in ['browsing_habits', 'purchase_history', 'brand_interactions', 
                         'device_usage', 'social_media_activity', 'content_consumption']:
                if persona['behavioral'][field]:
                    persona['behavioral'][field] = json.loads(persona['behavioral'][field])
        
        # Get contextual data
        cursor.execute("SELECT * FROM contextual_data WHERE persona_id = ?", (persona_id,))
        contextual = cursor.fetchone()
        if contextual:
            persona['contextual'] = dict(contextual)
    
    conn.close()
    return personas

def delete_persona(persona_id):
    """Delete a persona and all its associated data from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Delete the persona (CASCADE will handle related records)
        cursor.execute("DELETE FROM personas WHERE id = ?", (persona_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_persona(persona_id):
    """Retrieve a specific persona with all its data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get persona basic info
    cursor.execute("SELECT * FROM personas WHERE id = ?", (persona_id,))
    persona = dict(cursor.fetchone())
    
    # Get demographic data
    cursor.execute("SELECT * FROM demographic_data WHERE persona_id = ?", (persona_id,))
    demographic = cursor.fetchone()
    if demographic:
        persona['demographic'] = dict(demographic)
    
    # Get psychographic data
    cursor.execute("SELECT * FROM psychographic_data WHERE persona_id = ?", (persona_id,))
    psychographic = cursor.fetchone()
    if psychographic:
        persona['psychographic'] = dict(psychographic)
        # Parse JSON fields
        for field in ['interests', 'personal_values', 'attitudes', 'opinions']:
            if persona['psychographic'][field]:
                persona['psychographic'][field] = json.loads(persona['psychographic'][field])
    
    # Get behavioral data
    cursor.execute("SELECT * FROM behavioral_data WHERE persona_id = ?", (persona_id,))
    behavioral = cursor.fetchone()
    if behavioral:
        persona['behavioral'] = dict(behavioral)
        # Parse JSON fields
        for field in ['browsing_habits', 'purchase_history', 'brand_interactions', 
                     'device_usage', 'social_media_activity', 'content_consumption']:
            if persona['behavioral'][field]:
                persona['behavioral'][field] = json.loads(persona['behavioral'][field])
    
    # Get contextual data
    cursor.execute("SELECT * FROM contextual_data WHERE persona_id = ?", (persona_id,))
    contextual = cursor.fetchone()
    if contextual:
        persona['contextual'] = dict(contextual)
    
    conn.close()
    return persona

def save_archived_website(url, persona_id=None, archive_type='filesystem', archive_location=None):
    """
    Save an archived website to the database
    
    Args:
        url: The URL of the website (URI-R)
        persona_id: The ID of the persona used to visit the website (optional)
        archive_type: The type of archive (filesystem, postgres, internet_archive)
        archive_location: The path or identifier for the archive
    
    Returns:
        The ID of the newly created archived website
    """
    if not archive_location:
        # Create a default archive location based on a hash of the URL
        import hashlib
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
            (
                url,
                persona_id,
                archive_type,
                archive_location,
                datetime.now()
            )
        )
        
        archived_website_id = cursor.lastrowid
        conn.commit()
        return archived_website_id
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def save_memento(archived_website_id, memento_location, http_status=None, 
                content_type=None, content_length=None, headers=None, 
                screenshot_path=None, internet_archive_id=None):
    """
    Save a memento for an archived website
    
    Args:
        archived_website_id: The ID of the archived website
        memento_location: The path or identifier for this specific memento
        http_status: The HTTP status code of the response
        content_type: The Content-Type of the response
        content_length: The size of the archived content
        headers: JSON string of response headers
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

def get_archived_website(archived_website_id):
    """
    Retrieve a specific archived website with its associated persona
    
    Args:
        archived_website_id: The ID of the archived website
    
    Returns:
        Dictionary containing the archived website data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT aw.*, p.name as persona_name
    FROM archived_websites aw
    LEFT JOIN personas p ON aw.persona_id = p.id
    WHERE aw.id = ?
    """, (archived_website_id,))
    
    archived_website = cursor.fetchone()
    if not archived_website:
        conn.close()
        return None
    
    result = dict(archived_website)
    conn.close()
    return result

def get_all_archived_websites():
    """
    Retrieve all archived websites with their associated personas
    
    Returns:
        List of dictionaries containing archived website data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT aw.*, p.name as persona_name
    FROM archived_websites aw
    LEFT JOIN personas p ON aw.persona_id = p.id
    ORDER BY aw.created_at DESC
    """)
    
    archived_websites = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return archived_websites

def get_mementos_for_website(archived_website_id):
    """
    Retrieve all mementos for a specific archived website
    
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
    
    # Parse JSON fields
    for memento in mementos:
        if memento['headers']:
            memento['headers'] = json.loads(memento['headers'])
    
    conn.close()
    return mementos

def get_memento(memento_id):
    """
    Retrieve a specific memento
    
    Args:
        memento_id: The ID of the memento
    
    Returns:
        Dictionary containing the memento data
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
    
    # Parse JSON fields
    if result['headers']:
        result['headers'] = json.loads(result['headers'])
    
    conn.close()
    return result

# Initialize the database when the module is imported
init_db()
