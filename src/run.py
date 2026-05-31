from pathlib import Path
from . import DbWrapper

if __name__ == "__main__":
    # Check if we're running from the project root
    if not Path.cwd().resolve() == Path(__file__).resolve().parent.parent:
        print("Please run this script from the project root directory.")
        exit(1)

    # Create an empty database
    db = DbWrapper('test.db')
    ok = db.create_db(overwrite=True)
    if not ok:
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

    with db.session() as cursor:
        while cmds:
            sql = cmds.pop(0)
            db.command_history.append(sql)
            db.test_and_execute_sql_command(cursor, sql)
    