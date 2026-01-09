from ck3_mod_manager.database.launcher_db import LauncherDB
import pytest
import os

# Skip if DB doesn't exist (e.g. CI environment), but here we know it exists.
# We will use the actual DB for read tests, but avoid writing to it to not mess up user's data.
# Or better, check if we can read.

def test_launcher_db_read():
    db = LauncherDB()
    if not db.db_path.exists():
        pytest.skip("Launcher DB not found")
        
    db.connect()
    
    playsets = db.get_playsets()
    assert isinstance(playsets, list)
    # If there are playsets, check structure
    if playsets:
        ps = playsets[0]
        assert 'id' in ps
        assert 'name' in ps
        
        mods = db.get_mods_for_playset(ps['id'])
        assert isinstance(mods, list)
    
    db.close()
