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
    """Retrieve all personas from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT p.id, p.name, p.created_at, p.updated_at,
           d.latitude, d.longitude, d.language, d.country, d.city, d.region
    FROM personas p
    LEFT JOIN demographic_data d ON p.id = d.persona_id
    ORDER BY p.updated_at DESC
    """)
    
    personas = [dict(row) for row in cursor.fetchall()]
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

# Initialize the database when the module is imported
init_db()
