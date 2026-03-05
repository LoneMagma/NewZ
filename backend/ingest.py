import sqlite3
import feedparser
from datetime import datetime, timezone
from config import RSS_FEEDS
from database import get_connection


def fetch_and_store():
    conn = get_connection()
    cursor = conn.cursor()
    new_count = 0

    for feed_info in RSS_FEEDS:
        print(f"Fetching {feed_info['name']}...")
        try:
            feed = feedparser.parse(feed_info["url"])

            for entry in feed.entries[:20]:
                title     = entry.get("title", "").strip()
                url       = entry.get("link", "").strip()
                published = entry.get("published", str(datetime.now(timezone.utc)))
                summary   = entry.get("summary", "")

                if not title or not url:
                    continue

                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO articles
                            (title, source, url, published_at, region, raw_text)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (title, feed_info["name"], url, published, feed_info["region"], summary))

                    if cursor.rowcount > 0:
                        new_count += 1

                except sqlite3.Error as e:
                    print(f"  DB error: {e}")

        except Exception as e:
            print(f"  Failed to fetch {feed_info['name']}: {e}")

    conn.commit()
    conn.close()
    print(f"Done. {new_count} new articles stored.")


if __name__ == "__main__":
    from database import init_db
    init_db()
    fetch_and_store()
