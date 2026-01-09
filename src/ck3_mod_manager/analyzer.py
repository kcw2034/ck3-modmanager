import os
import zipfile
from pathlib import Path
from typing import List, Dict, Set

class ModAnalyzer:
    def __init__(self):
        self._cache: Dict[str, Set[str]] = {}

    def get_mod_files(self, mod: Dict) -> Set[str]:
        """
        Extracts a set of relative file paths from a mod.
        Supports both directory and zip archive mods.
        Uses in-memory caching to avoid re-reading files.
        """
        mod_id = str(mod.get('mod_id'))
        # Return cached result if available
        if mod_id in self._cache:
            return self._cache[mod_id]

        files = set()
        
        # Check for archive path (Zip)
        archive_path = mod.get('archivePath')
        if archive_path:
            path = Path(archive_path)
            if path.exists() and zipfile.is_zipfile(path):
                try:
                    with zipfile.ZipFile(path, 'r') as zip_ref:
                        # List all files in zip
                        for name in zip_ref.namelist():
                            # Normalize path separators
                            normalized_name = name.replace('\\', '/')
                            # Filter out directories and irrelevant files (e.g., descriptor.mod)
                            if not normalized_name.endswith('/') and not normalized_name.endswith('.mod'):
                                files.add(normalized_name)
                except Exception as e:
                    print(f"Error reading zip {path}: {e}")

        # Check for directory path
        dir_path = mod.get('dirPath')
        if dir_path:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                try:
                    for root, _, filenames in os.walk(path):
                        for filename in filenames:
                            # Skip .mod files and hidden files
                            if filename.endswith('.mod') or filename.startswith('.'):
                                continue
                                
                            full_path = Path(root) / filename
                            rel_path = full_path.relative_to(path).as_posix()
                            files.add(rel_path)
                except Exception as e:
                    print(f"Error reading directory {path}: {e}")
        
        # Cache the result
        self._cache[mod_id] = files
        return files


    def analyze_conflicts(self, mods: List[Dict]) -> Dict[str, List[str]]:
        """
        Analyzes a list of mods for file conflicts.
        Returns a dictionary mapping relative file paths to a list of mod names that modify them.
        Only includes files modified by 2 or more mods.
        """
        file_map: Dict[str, List[str]] = {}
        
        for mod in mods:
            mod_name = mod.get('displayName') or mod.get('name') or "Unknown Mod"
            mod_files = self.get_mod_files(mod)
            
            for file_path in mod_files:
                if file_path not in file_map:
                    file_map[file_path] = []
                file_map[file_path].append(mod_name)
        
        # Filter strictly for conflicts (files appearing in > 1 mod)
        conflicts = {path: names for path, names in file_map.items() if len(names) > 1}
        return conflicts
