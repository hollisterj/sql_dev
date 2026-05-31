from pathlib import Path
import sqlite3
from typing import Any, Optional
from contextlib import contextmanager
from . import Logger
class DbWrapper:
    DB_DIR = Path('./db/')

    """
    A simple wrapper class to hold the connection and cursor together.
    This can be useful if you want to pass around a single object instead of separate conn/cursor.
    """
    def __init__(self, name: str):
        self.db_path = DbWrapper.DB_DIR / name
        self.command_history = []
        self.log = Logger(name=f"{self.__class__.__name__}({name})", label=name)

    @contextmanager
    def session(self):
        """
        Custom context manager that opens a connection, creates a cursor,
        automatically commits/rolls back, and guarantees connection closure.
        """
        # 1. Setup / Connect
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        self.log.info("Database connection opened.")
        
        try:
            # 2. Yield the cursor back to the 'with' block
            yield cursor
            
        except sqlite3.Error as e:
            # 4. If any database error happened, undo the changes
            conn.rollback()
            self.log.error(f"Transaction rolled back due to error: {e}")
            raise # Re-raise the error so the main application knows it failed
            
        finally:
            # 5. Teardown / Always close the connection
            conn.close()
            self.log.info("Database connection closed.")

    def create_db(self, overwrite:bool = False) -> tuple[bool, Optional[Path]]:
        
        if self.db_path.exists():
            if not overwrite:
                self.log.error(f"Database {self.db_path} already exists. Use overwrite=True to recreate it.")
                return False
            else:
                self.log.debug(f"Overwriting existing database {self.db_path}...")
                self.db_path.unlink()  # Remove the existing file
        
        # Create and close
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.close()
            self.log.info(f"Database {self.db_path} created successfully!")
        except sqlite3.Error as e:
            self.log.error(f"Failed to create database {self.db_path}: {e}")
            return False
        return True
    
    def dry_run(self, db_cursor: sqlite3.Cursor, sql: str, params: tuple[Any, ...] = ()) -> tuple[bool, Optional[str]]:
        """
        Tests ANY SQL command (including CREATE TABLE) by safely copying 
        the schema to a temporary in-memory database.
        """

        self.log.debug(f"{sql}")

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
        
        if success:
            self.log.debug("Pass")
        else:
            self.log.info(f"{sql}")
            self.log.error(f"Fail - {error_message}")
        return success, error_message

    def execute(self, db_cursor: sqlite3.Cursor, sql: str, params: tuple[Any, ...] = ()) -> bool:
        """
        Executes a SQL command on the real database. Use this after testing with dry_run.
        """
        self.log.info(f"{sql}")
        try:
            db_cursor.execute(sql, params)
            db_cursor.connection.commit()
            success = True
        except sqlite3.Error as e:
            self.log.error(f"Failed - {e}")
            success = False
        if success:
            self.log.info(f"Success\n")
        else:
            self.log.error(f"Failure: {e}\n")
        return success

    def test_and_execute_sql_command(self, db_cursor: sqlite3.Cursor, sql: str, params: tuple[Any, ...] = ()) -> bool:
        """
        Combines testing and executing a SQL command. First tests the command on an isolated memory DB,
        and if it succeeds, executes it on the real database.
        """
        ok, err = self.dry_run(db_cursor, sql, params)
        if not ok:
            self.log.error(f"Test failed for command: {sql}. Error: {err}")
            return False
        
        return self.execute(db_cursor, sql, params)