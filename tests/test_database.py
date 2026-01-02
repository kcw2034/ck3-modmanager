from ck3_mod_manager.main import CK3ModDatabase
from ck3_mod_manager.utils.config import DB_PATH

db = CK3ModDatabase(DB_PATH)
db.connect()

tables = db.get_tables()
print(tables)