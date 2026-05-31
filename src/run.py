import cmd
from pathlib import Path
import sqlite3
from typing import Any, Optional
from contextlib import contextmanager
from . import create_db, test_sql_command, db_session

if __name__ == "__main__":
    # Check if we're running from the project root
    if not Path.cwd().resolve() == Path(__file__).resolve().parent.parent:
        print("Please run this script from the project root directory.")
        exit(1)

    # Create an empty database
    ok, db_path = create_db('test.db', overwrite=True)
    if not ok or db_path is None:
        print("Failed to create database. Exiting.")
        exit(1)
    
    # Populate the contents of the db
    cmds = [
        """CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER);
        """,
    "INSERT INTO users (name, age) VALUES ('Alice', 30);",
    "INSERT INTO users (name, age) VALUES ('Bob', 25);",
    ]

    with db_session(db_path) as cursor:
        for cmd in cmds:
            print(f"Attempting command: {cmd}", end=' ... ')
            ok, err = test_sql_command(cursor, cmd)
            if not ok:
                print("Test failed. Exiting command loop")
                break
            cursor.execute(cmd)
            cursor.connection.commit()
            print("Command executed successfully.")
    