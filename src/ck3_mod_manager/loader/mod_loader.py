import os
import re
from pathlib import Path
from typing import List, Dict, Optional

class ModLoader:
    def __init__(self):
        self.documents_path = Path(os.path.expanduser("~/Documents/Paradox Interactive/Crusader Kings III"))
        self.mod_path = self.documents_path / "mod"
        self.steam_path = Path(os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/1158310"))
        self.mods: List[Dict] = []

    def load_mods(self) -> List[Dict]:
        """Scans for mods and returns a list of mod dictionaries."""
        self.mods = []
        
        # 1. Scan local .mod files in Documents/mod
        if self.mod_path.exists():
            for file_path in self.mod_path.glob("*.mod"):
                mod_data = self._parse_mod_file(file_path)
                if mod_data:
                    mod_data['is_local'] = True
                    mod_data['descriptor_path'] = str(file_path)
                    self.mods.append(mod_data)

        # 2. Scan Steam Workshop mods (Optional logic, usually handled by checking .mod files in docs that point to workshop)
        # CK3 launcher creates .mod files in documents/mod for subscribed steam mods too. 
        # So primarily scanning documents/mod is enough for enabled/disabled status, 
        # but we might need to read actual workshop folder for more details if the .mod file is a pointer in the future.
        # For now, let's rely on what's in Documents/mod as that's what the game reads.
        
        return self.mods

    def _parse_mod_file(self, file_path: Path) -> Optional[Dict]:
        """Parses a Paradox .mod file (key=value format)."""
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic parsing using regex or simple line split
            # Format is usually: name="Mod Name" path="mod/..." or supported_version="1.12.*"
            
            name_match = re.search(r'name\s*=\s*"(.*?)"', content)
            if name_match:
                data['name'] = name_match.group(1)
            else:
                data['name'] = file_path.stem

            path_match = re.search(r'path\s*=\s*"(.*?)"', content)
            if path_match:
                raw_path = path_match.group(1)
                # handle relative path
                if not os.path.isabs(raw_path):
                     # Usually relative to user documents/Paradox Interactive/Crusader Kings III
                     # But local mods often have path="mod/my_mod"
                     pass
                data['path'] = raw_path
            
            version_match = re.search(r'supported_version\s*=\s*"(.*?)"', content)
            if version_match:
                data['version'] = version_match.group(1)
            
            remote_id_match = re.search(r'remote_file_id\s*=\s*"(.*?)"', content)
            if remote_id_match:
                data['remote_file_id'] = remote_id_match.group(1)

            return data

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def save_load_order(self, mod_list: List[Dict]):
        """
        Saves the load order. 
        In CK3, load order is managed by 'dlc_load.json' or 'launcher-v2.sqlite'.
        Editing dlc_load.json is the simplest way to force a load order (used by barebones launcher mode)
        or we might need to update the sqlite db if we want to sync with the official launcher.
        
        For this simplified version, let's try to update 'dlc_load.json' if it exists, 
        or just print the order for now as a first step.
        """
        dlc_load_path = self.documents_path / "dlc_load.json"
        
        # Format for dlc_load.json:
        # {"disabled_dlcs":[],"enabled_mods":["mod/ugc_12345.mod", "mod/local_mod.mod"]}
        
        enabled_mods = [mod['descriptor_path'] for mod in mod_list if mod.get('enabled', False)]
        
        import json
        data = {"disabled_dlcs": [], "enabled_mods": enabled_mods}
        
        try:
            with open(dlc_load_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"Saved load order to {dlc_load_path}")
        except Exception as e:
            print(f"Failed to save load order: {e}")

