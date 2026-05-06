import sqlite3
import os
import sys

if getattr(sys, 'frozen', False):
    # Si es ejecutable (.exe)
    app_dir = os.path.dirname(sys.executable)
else:
    # Si es script (dev)
    app_dir = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(app_dir, "config_local.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_setting(key, default=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["value"]
    return default


def set_setting(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, str(value))
    )
    conn.commit()
    conn.close()


def get_all_settings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}


def is_firebase_configured():
    cred_path = get_setting("firebase_credentials_path")
    project_id = get_setting("firebase_project_id")
    return bool(cred_path and project_id)


def delete_setting(key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
    conn.commit()
    conn.close()


init_db()
