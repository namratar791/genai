"""
db/database.py
Context manager for the SQLite connection.

Always connects to the permanent file DB defined by DATABASE_URL in .env
(default: sqlite:///./db/nlq_app.db). Auto-creates + seeds it on first use,
and never deletes/resets it — it persists across restarts.

Usage:
    from db.database import get_db_connection

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers LIMIT 5")
        rows = cur.fetchall()
"""

import os
import sqlite3
from contextlib import contextmanager

from db.schema import create_all_tables
from db.seed_data import (seed_all, seed_table_descriptions)
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # nlq-app/
DB_MODE = os.getenv("DB_MODE")
DB_CONN = None

def _resolve_sqlite_path(database_url: str) -> str:
    """
    Turns a standard sqlite:/// URL into an actual filesystem path.
    'sqlite:///./db/nlq_app.db' -> '<project_root>/db/nlq_app.db'
    """
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError(
            f"Unsupported DATABASE_URL: '{database_url}'. "
            f"Only sqlite:///<path> is supported right now (e.g. sqlite:///./db/nlq_app.db)."
        )
    relative_path = database_url[len(prefix):]  # './db/nlq_app.db'
    return os.path.normpath(os.path.join(PROJECT_ROOT, relative_path))


DB_PATH = _resolve_sqlite_path(DATABASE_URL)


def _init_if_needed(conn):
    """
    Creates any missing tables and seeds any empty ones. Safe to call on every
    connection: CREATE TABLE IF NOT EXISTS is a no-op for existing tables, and
    seed_all() individually checks each table before inserting into it.

    If two requests happen to hit this at the exact same moment on a brand-new
    database (rare, but possible with uvicorn --reload or two quick requests),
    both might see a table as "empty" and both try to insert -> the second one
    hits a UNIQUE constraint error. Treat that as "someone else already seeded
    it" and move on instead of failing the request.
    """
    create_all_tables(conn)
    try:
        seed_all(conn)
        seed_table_descriptions(conn)
    except sqlite3.IntegrityError:
        conn.rollback()  # discard this half-finished attempt; the other one already succeeded

def initialize_db():

    global DB_CONN

    if DB_CONN is not None:
        return

    if DB_MODE == "memory":

        DB_CONN = sqlite3.connect(
            ":memory:",
            check_same_thread=False
        )

    else:

        db_path = DATABASE_URL.replace(
            "sqlite:///",
            ""
        )

        DB_CONN = sqlite3.connect(
            db_path,
            check_same_thread=False
        )

    DB_CONN.row_factory = sqlite3.Row
    DB_CONN.execute(
        "PRAGMA foreign_keys = ON"
    )

    create_all_tables(DB_CONN)

    try:
        seed_all(DB_CONN)
        seed_table_descriptions(DB_CONN)

    except sqlite3.IntegrityError:
        DB_CONN.rollback()

@contextmanager
def get_db_connection():
    """Yields a sqlite3.Connection (row_factory=sqlite3.Row) to db/nlq_app.db."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        _init_if_needed(conn)
        yield conn
    finally:
        conn.close()


if __name__ == "__main__":
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print("Tables:", [r["name"] for r in cur.fetchall()])
        cur.execute("SELECT COUNT(*) AS n FROM customers;")
        print("Customer rows:", cur.fetchone()["n"])