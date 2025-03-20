import sqlite3

DB_PATH = 'personas.db'

def migrate_database():
    """Migrate the database to separate latitude and longitude fields."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Step 1: Create a new table with the updated schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS demographic_data_new (
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

        # Step 2: Copy data from the old table to the new table
        cursor.execute('SELECT * FROM demographic_data')
        rows = cursor.fetchall()
        for row in rows:
            # Extract latitude and longitude from the geolocation field
            geolocation = row[2]  # Assuming geolocation is the 3rd column
            latitude, longitude = None, None
            if geolocation:
                try:
                    latitude, longitude = map(float, geolocation.split(','))
                except ValueError:
                    pass  # Handle invalid geolocation format gracefully

            # Insert data into the new table
            cursor.execute('''
            INSERT INTO demographic_data_new (
                persona_id, latitude, longitude, language, country, city, region, age, gender, education, income, occupation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row[1],  # persona_id
                latitude,
                longitude,
                row[3],  # language
                row[4],  # country
                row[5],  # city
                row[6],  # region
                row[7],  # age
                row[8],  # gender
                row[9],  # education
                row[10], # income
                row[11]  # occupation
            ))

        # Step 3: Drop the old table and rename the new table
        cursor.execute('DROP TABLE demographic_data')
        cursor.execute('ALTER TABLE demographic_data_new RENAME TO demographic_data')

        conn.commit()
        print("Database migration completed successfully.")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
