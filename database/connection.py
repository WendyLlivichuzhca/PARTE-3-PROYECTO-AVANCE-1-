from contextlib import contextmanager
import sqlite3

from utils.app_paths import get_database_path


DB_PATH = get_database_path()


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        yield connection
        connection.commit()
    finally:
        connection.close()
