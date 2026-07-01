import sqlite3

from src.app.config import DATABASE_PATH


class DatabaseManager:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE_PATH)

        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            potholes INTEGER,
            longitudinal_cracks INTEGER,
            lateral_cracks INTEGER,
            alligator_cracks INTEGER,
            high_risk INTEGER,
            medium_risk INTEGER,
            low_risk INTEGER,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

        # Dynamic schema migration for older databases
        try:
            cursor.execute("ALTER TABLE detections ADD COLUMN latitude REAL")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass # column already exists

        try:
            cursor.execute("ALTER TABLE detections ADD COLUMN longitude REAL")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass # column already exists

    def insert_detection(
        self,
        image_name,
        potholes,
        longitudinal,
        lateral,
        alligator,
        high,
        medium,
        low,
        latitude=None,
        longitude=None
    ):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO detections (
            image_name,
            potholes,
            longitudinal_cracks,
            lateral_cracks,
            alligator_cracks,
            high_risk,
            medium_risk,
            low_risk,
            latitude,
            longitude
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            image_name,
            potholes,
            longitudinal,
            lateral,
            alligator,
            high,
            medium,
            low,
            latitude,
            longitude
        ))
        self.conn.commit()

    def get_all_detections(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, image_name, potholes, longitudinal_cracks, lateral_cracks, 
               alligator_cracks, high_risk, medium_risk, low_risk, latitude, longitude, created_at
        FROM detections
        ORDER BY created_at DESC
        """)
        return cursor.fetchall()

    def clear_database(self):

        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM detections")

        self.conn.commit()