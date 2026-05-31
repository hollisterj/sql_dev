from pathlib import Path

# Globals
DB_DIR = Path('./db/')

# Must go below DB_DIR to avoid circular imports
from .db_utils import create_db, test_sql_command, db_session
