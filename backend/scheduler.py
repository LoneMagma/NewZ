import time
import threading
from datetime import datetime
from database import get_connection, init_db
from ingest import fetch_and_store
from score import score_unscored_articles

BREAKING_KEYWORDS = [
    "rbi", "rate cut", "rate hike", "circuit breaker", "crash", "war",
    "ban", "sanction", "default", "collapse", "emergency", "halt",
    "sebi", "budget", "gdp", "inflation", "repo rate", "sensex crash",
]

BREAKING_INTERVAL = 300    # 5 minutes
FULL_SCAN_INTERVAL = 1800  # 30 minutes


def check_breaking_news():
    conn    = get_connection()
    cursor  = conn.cursor()
    cursor.execute("""
        SELECT id, title FROM articles
        WHERE relevance_score = 0
        AND fetched_at >= datetime('now', '-10 minutes')
    """)
    articles = cursor.fetchall()
    conn.close()

    urgent = [
        a["id"] for a in articles
        if any(kw in a["title"].lower() for kw in BREAKING_KEYWORDS)
    ]

    if urgent:
        print(f"[BREAKING] {len(urgent)} urgent articles detected — scoring immediately")
        score_unscored_articles()


def breaking_news_loop():
    while True:
        try:
            ts = datetime.now().strftime("%H:%M")
            print(f"[{ts}] Breaking news check...")
            fetch_and_store()
            check_breaking_news()
        except Exception as e:
            print(f"Breaking check error: {e}")
        time.sleep(BREAKING_INTERVAL)


def full_scan_loop():
    while True:
        try:
            ts = datetime.now().strftime("%H:%M")
            print(f"[{ts}] Full scan...")
            score_unscored_articles()
        except Exception as e:
            print(f"Full scan error: {e}")
        time.sleep(FULL_SCAN_INTERVAL)


def start_scheduler():
    init_db()
    print("Scheduler starting...")

    t1 = threading.Thread(target=breaking_news_loop, daemon=True)
    t2 = threading.Thread(target=full_scan_loop,     daemon=True)

    t1.start()
    t2.start()
    print("Loops running — breaking (5 min) + full scan (30 min)")
