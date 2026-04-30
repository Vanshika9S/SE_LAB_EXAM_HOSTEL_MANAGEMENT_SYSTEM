import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "hostel.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     TEXT PRIMARY KEY,
            password    TEXT NOT NULL,
            name        TEXT NOT NULL,
            role        TEXT NOT NULL CHECK(role IN ('student', 'complaint_manager')),
            is_active   INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id    TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            category        TEXT NOT NULL,
            description     TEXT NOT NULL,
            photo_path      TEXT,
            status          TEXT NOT NULL DEFAULT 'Pending',
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );

        INSERT OR IGNORE INTO users VALUES ('S001', 'pass123', 'Alice Student', 'student', 1);
        INSERT OR IGNORE INTO users VALUES ('S002', 'pass456', 'Bob Student',   'student', 0);
        INSERT OR IGNORE INTO users VALUES ('M001', 'mgr789', 'Carol Manager', 'complaint_manager', 1);
    """)

    conn.commit()
    conn.close()