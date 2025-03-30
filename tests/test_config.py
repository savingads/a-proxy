"""
Test configuration and utilities for A-Proxy tests.
This module provides common test fixtures and mock data for tests.
"""

import tempfile
import os
import json
import sqlite3
from datetime import datetime

# Sample test persona data that can be used across tests
SAMPLE_PERSONA = {
    "name": "Test Persona",
    "demographic": {
        "geolocation": "40.7128, -74.0060",
        "language": "en-US",
        "country": "United States",
        "city": "New York",
        "region": "NY",
        "age": 30,
        "gender": "Female",
        "education": "Bachelor's",
        "income": "100000",
        "occupation": "Software Engineer"
    },
    "psychographic": {
        "interests": ["technology", "travel", "food"],
        "personal_values": ["privacy", "freedom", "innovation"],
        "attitudes": ["environmentally conscious"],
        "lifestyle": "Urban professional",
        "personality": "Analytical",
        "opinions": ["pro technology regulation"]
    },
    "behavioral": {
        "browsing_habits": ["news sites", "technology blogs"],
        "purchase_history": ["electronics", "books"],
        "brand_interactions": ["Apple", "Amazon"],
        "device_usage": {"mobile": 60, "desktop": 40},
        "social_media_activity": {"Twitter": "high", "Instagram": "medium"},
        "content_consumption": {"articles": "high", "videos": "medium"}
    },
    "contextual": {
        "time_of_day": "Morning",
        "day_of_week": "Weekday",
        "season": "Spring",
        "weather": "Sunny",
        "device_type": "Mobile",
        "browser_type": "Chrome",
        "screen_size": "Small",
        "connection_type": "Wifi"
    }
}

# Sample IP info response for mock testing
SAMPLE_IP_INFO = {
    "ip": "203.0.113.1",
    "hostname": "example.host.com",
    "city": "New York",
    "region": "NY",
    "country": "US",
    "loc": "40.7128,-74.0060",
    "org": "Example ISP"
}

def create_temp_db():
    """Create a temporary database file for testing"""
    db_fd, db_path = tempfile.mkstemp()
    return db_fd, db_path

def init_test_db(db_path):
    """Initialize a test database with tables"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create tables
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

def cleanup_temp_db(db_fd, db_path):
    """Clean up temporary database"""
    os.close(db_fd)
    os.unlink(db_path)

def insert_test_persona(db_path, persona_data=None):
    """Insert a test persona into the database and return its ID"""
    if persona_data is None:
        persona_data = SAMPLE_PERSONA
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Insert persona record
    cursor.execute(
        "INSERT INTO personas (name, created_at, updated_at) VALUES (?, ?, ?)",
        (persona_data.get('name', 'Test Persona'), 
         datetime.now(), 
         datetime.now())
    )
    persona_id = cursor.lastrowid
    
    # Insert demographic data
    demographic = persona_data.get('demographic', {})
    
    # Parse geolocation string into latitude and longitude if it exists
    latitude = None
    longitude = None
    geolocation = demographic.get('geolocation', '')
    if geolocation and ',' in geolocation:
        try:
            lat_str, lng_str = geolocation.split(',', 1)
            latitude = float(lat_str.strip())
            longitude = float(lng_str.strip())
        except (ValueError, TypeError):
            # If parsing fails, leave latitude and longitude as None
            pass
    
    cursor.execute(
        """
        INSERT INTO demographic_data 
        (persona_id, latitude, longitude, language, country, city, region, age, gender, education, income, occupation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            persona_id,
            latitude,
            longitude,
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
    conn.close()
    
    return persona_id
