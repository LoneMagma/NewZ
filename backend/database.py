import sqlite3
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            title            TEXT NOT NULL,
            source           TEXT,
            url              TEXT UNIQUE,
            published_at     TEXT,
            region           TEXT,
            tier             INTEGER DEFAULT 2,
            raw_text         TEXT,
            relevance_score  INTEGER DEFAULT 0,
            relevance_reason TEXT,
            sector_score     INTEGER DEFAULT 0,
            geo_score        INTEGER DEFAULT 0,
            urgency_score    INTEGER DEFAULT 0,
            key_topics       TEXT,
            named_entities   TEXT,
            fetched_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id          INTEGER PRIMARY KEY,
            role        TEXT,
            location    TEXT,
            sectors     TEXT,
            watching    TEXT,
            sensitivity INTEGER DEFAULT 5
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            action     TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles(id)
        )
    """)

    # migrate — add any missing columns safely
    existing = [r[1] for r in cursor.execute("PRAGMA table_info(articles)").fetchall()]
    migrations = [
        ("sector_score",   "INTEGER DEFAULT 0"),
        ("geo_score",      "INTEGER DEFAULT 0"),
        ("urgency_score",  "INTEGER DEFAULT 0"),
        ("tier",           "INTEGER DEFAULT 2"),
        ("key_topics",     "TEXT"),
        ("named_entities", "TEXT"),
    ]
    for col, typedef in migrations:
        if col not in existing:
            cursor.execute(f"ALTER TABLE articles ADD COLUMN {col} {typedef}")
            print(f"  Migrated: added column {col}")

    conn.commit()
    conn.close()
    print("Database ready.")


if __name__ == "__main__":
    init_db()
