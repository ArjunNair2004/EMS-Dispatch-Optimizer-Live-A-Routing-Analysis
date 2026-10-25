import sqlite3
import csv
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_name="ems_logs.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dispatch_logs (
                dispatch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                hazard_type TEXT,
                location TEXT,
                base_eta INTEGER,
                detour_eta INTEGER,
                time_saved INTEGER
            )
        ''')
        self.conn.commit()

    def log_dispatch(self, hazard_type, location, base_eta, detour_eta):
        penalty = 45 if hazard_type == "Accident" else 15 if hazard_type == "Construction" else 10
        time_saved = (base_eta + penalty) - detour_eta
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO dispatch_logs (timestamp, hazard_type, location, base_eta, detour_eta, time_saved)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, hazard_type, location, base_eta, detour_eta, time_saved))
        self.conn.commit()

    def export_to_csv(self, filename="ems_dispatch_report.csv"):
        self.cursor.execute("SELECT * FROM dispatch_logs")
        rows = self.cursor.fetchall()
        
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Dispatch ID", "Timestamp", "Hazard Type", "Location", "Base ETA", "Detour ETA", "Time Saved"])
            writer.writerows(rows)

    def clear_database(self):
        self.cursor.execute("DELETE FROM dispatch_logs")
        self.conn.commit()