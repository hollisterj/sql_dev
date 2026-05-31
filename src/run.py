from pathlib import Path
import sqlite3
from typing import Any, Optional
from contextlib import contextmanager
from . import create_db, test_sql_command, db_session

if __name__ == "__main__":
    if not Path.cwd().resolve() == Path(__file__).resolve().parent.parent:
        print("Please run this script from the project root directory.")
        exit(1)
    conn = create_db('test.db', overwrite=True)
