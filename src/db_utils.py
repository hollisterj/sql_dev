from pathlib import Path
import sqlite3
from typing import Any, Optional
from contextlib import contextmanager
from . import DB_DIR

@contextmanager
def db_session(db_path: Path):
    """
    Custom context manager that opens a connection, creates a cursor,
    automatically commits/rolls back, and guarantees connection closure.
    """
    # 1. Setup / Connect
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 2. Yield the cursor back to the 'with' block
        yield cursor
        
    except sqlite3.Error as e:
        # 4. If any database error happened, undo the changes
        conn.rollback()
        print(f"Transaction rolled back due to error: {e}")
        raise # Re-raise the error so the main application knows it failed
        
    finally:
        # 5. Teardown / Always close the connection
        conn.close()
        print("Database connection closed.")


def test_sql_command(db_cursor: sqlite3.Cursor, sql: str, params: tuple[Any, ...] = ()) -> tuple[bool, Optional[str]]:
    """
    Tests ANY SQL command (including CREATE TABLE) by safely copying 
    the schema to a temporary in-memory database. Your real file is never touched.
    """

    # 2. Create a completely isolated, temporary database in RAM
    test_conn = sqlite3.connect(":memory:")
    
    try:
        # 3. Clone the existing schema from your real DB to the memory DB
        # This ensures the test DB has all the same tables and structures
        real_conn = db_cursor.connection
        real_conn.backup(test_conn)
        
        # 4. Try running the command on the isolated memory database
        test_cursor = test_conn.cursor()
        test_cursor.execute(sql, params)
        
        # If it's a SELECT, verify it can fetch
        if sql.strip().upper().startswith("SELECT"):
            test_cursor.fetchone()
            
        success = True
        error_message = None
        
    except sqlite3.Error as e:
        success = False
        error_message = str(e)
        
    finally:
        # 5. Clean up. Closing the memory connection instantly wipes it from RAM.
        test_conn.close()
        
    return success, error_message


def create_db(name:str ="test.db", overwrite:bool = False) -> tuple[bool, Optional[Path]]:
    
    db_target = DB_DIR / name
    if db_target.exists():
        if not overwrite:
            print(f"Database {name} already exists. Use overwrite=True to recreate it.")
            return False, None
        else:
            print(f"Overwriting existing database {name}...")
            db_target.unlink()  # Remove the existing file
    
    # Create and close
    try:
        conn = sqlite3.connect(str(db_target))
        conn.close()
        print(f"Database {DB_DIR}\\{name} created successfully!")
    except sqlite3.Error as e:
        print(f"Failed to create database {name}: {e}")
        return False, None
    return True, db_target
