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
        
        # 3. If no errors occurred in the 'with' block, commit the changes
        conn.commit()
        print("Transaction committed successfully.")
        
    except sqlite3.Error as e:
        # 4. If any database error happened, undo the changes
        conn.rollback()
        print(f"Transaction rolled back due to error: {e}")
        raise # Re-raise the error so the main application knows it failed
        
    finally:
        # 5. Teardown / Always close the connection
        conn.close()
        print("Database connection closed.")

def create_db(name:str ="my_database.db", overwrite:bool = False):
       
    db_target = DB_DIR / name
    if db_target.exists():
        if not overwrite:
            print(f"Database {name} already exists. Use overwrite=True to recreate it.")
            return None
        else:
            print(f"Overwriting existing database {name}...")
            db_target.unlink()  # Remove the existing file
    
    # Create and close
    conn = sqlite3.connect(str(db_target))
    conn.close()
    print(f"Database {DB_DIR}\\{name} created successfully!")
    return conn

def test_sql_command(db_path: str, sql: str, params: tuple[Any, ...] = ()) -> tuple[bool, Optional[str]]:
    """
    Tests an SQL command against the database without saving changes.
    
    Returns:
        (True, None) if the command is valid and runs successfully.
        (False, "Error Message") if the command fails.
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Start a manual transaction block
        cursor.execute("BEGIN TRANSACTION;")
        
        # 2. Try executing the user's command
        cursor.execute(sql, params)
        
        # If it's a SELECT statement, we can even test if fetching works
        if sql.strip().upper().startswith("SELECT"):
            cursor.fetchone()
            
        success = True
        error_message = None
        
    except sqlite3.Error as e:
        # If SQLite rejects the command for any reason, catch the error
        success = False
        error_message = str(e)
        
    finally:
        # 3. CRITICAL: Rollback everything. 
        # Even if the SQL succeeded, we undo it so it acts as a test.
        conn.rollback()
        conn.close()
        
    return success, error_message
