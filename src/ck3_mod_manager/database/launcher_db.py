import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Optional

class LauncherDB:
    def __init__(self):
        self.db_path = Path(os.path.expanduser("~/Documents/Paradox Interactive/Crusader Kings III/launcher-v2.sqlite"))
        self.conn = None

    def connect(self):
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()

    def get_playsets(self) -> List[Dict]:
        """Fetch all playsets."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM playsets ORDER BY createdOn DESC")
        return [dict(row) for row in cursor.fetchall()]

    def get_active_playset(self) -> Optional[Dict]:
        """Fetch the currently active playset."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM playsets WHERE isActive = 1 LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None

    def set_active_playset(self, playset_id: str):
        """Set a playset as active."""
        cursor = self.conn.cursor()
        with self.conn:
            cursor.execute("UPDATE playsets SET isActive = 0")
            cursor.execute("UPDATE playsets SET isActive = 1 WHERE id = ?", (playset_id,))

    def get_mods_for_playset(self, playset_id: str) -> List[Dict]:
        """Fetch mods for a playset, ordered by position."""
        query = """
        SELECT 
            m.id as mod_id,
            m.displayName,
            m.name,
            m.version,
            m.dirPath,
            m.archivePath,
            m.thumbnailPath,
            pm.enabled,
            pm.position
        FROM playsets_mods pm
        JOIN mods m ON pm.modId = m.id
        WHERE pm.playsetId = ?
        ORDER BY pm.position ASC
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (playset_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_mods(self) -> List[Dict]:
        """Fetch all available mods from the database."""
        query = """
        SELECT 
            id as mod_id,
            displayName,
            name,
            version,
            dirPath,
            archivePath,
            thumbnailPath
        FROM mods
        ORDER BY displayName ASC
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    
    def remove_mod_from_playset(self, playset_id, mod_id):
        """Removes a mod from the specified playset."""
        try:
            with self.conn:
                self.conn.execute("DELETE FROM playsets_mods WHERE playsetId = ? AND modId = ?", 
                                  (playset_id, mod_id))
            return True
        except sqlite3.Error as e:
            print(f"Error removing mod from playset: {e}")
            return False

    def add_mod_to_playset(self, playset_id: str, mod_id: str) -> bool:
        """Add a mod to the playset. Returns True if added, False if already exists."""
        cursor = self.conn.cursor()
        
        # Check if already exists
        cursor.execute("SELECT 1 FROM playsets_mods WHERE playsetId = ? AND modId = ?", (playset_id, mod_id))
        if cursor.fetchone():
            return False
            
        # Get next position
        cursor.execute("SELECT MAX(position) FROM playsets_mods WHERE playsetId = ?", (playset_id,))
        row = cursor.fetchone()
        next_pos = (row[0] + 1) if row and row[0] is not None else 0
        
        with self.conn:
            cursor.execute("""
                INSERT INTO playsets_mods (playsetId, modId, enabled, position)
                VALUES (?, ?, ?, ?)
            """, (playset_id, mod_id, 1, next_pos)) # Default enabled
            
        return True

    def update_playset_mods(self, playset_id: str, mods_data: List[Dict]):
        """
        Update enabled state and position for mods in a playset.
        mods_data should be a list of dicts with 'mod_id' and 'enabled', in the desired order.
        """
        cursor = self.conn.cursor()
        with self.conn:
            for index, mod in enumerate(mods_data):
                cursor.execute("""
                    UPDATE playsets_mods 
                    SET enabled = ?, position = ?
                    WHERE playsetId = ? AND modId = ?
                """, (mod['enabled'], index, playset_id, mod['mod_id']))

