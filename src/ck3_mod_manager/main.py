import sqlite3
from pathlib import Path
from typing import List

class CK3ModDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def get_tables(self) -> List[str]:
        """Get a list of table names in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return cursor.fetchall()