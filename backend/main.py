import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from database import get_connection, init_db
from scheduler import start_scheduler

app = FastAPI(title="NewZ API v1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.on_event("startup")
def startup():
    init_db()
    thread = threading.Thread(target=start_scheduler, daemon=True)
    thread.start()


@app.get("/")
def serve_frontend():
    return FileResponse("../frontend/index.html")


# ── ARTICLES ──────────────────────────────────────────────────────────────────

@app.get("/articles")
def get_articles(min_score: int = 0, limit: int = 300):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, source, url, published_at, region, tier,
               relevance_score, relevance_reason,
               urgency_score, key_topics, named_entities
        FROM articles
        WHERE relevance_score >= ?
        AND   relevance_score != -1
        ORDER BY fetched_at DESC
        LIMIT ?
    """, (min_score, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/articles/breaking")
def get_breaking():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, source, url, published_at, region,
               relevance_score, relevance_reason,
               urgency_score, key_topics, named_entities
        FROM articles
        WHERE urgency_score >= 8
        AND   relevance_score != -1
        AND   fetched_at >= datetime('now', '-2 hours')
        ORDER BY urgency_score DESC, fetched_at DESC
        LIMIT 15
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── PROFILE ───────────────────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    role:        str
    location:    str
    sectors:     str
    watching:    str
    sensitivity: int = 5


@app.get("/profile")
def get_profile():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


@app.post("/profile")
def save_profile(data: ProfileUpdate):
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO user_profile
            (id, role, location, sectors, watching, sensitivity)
        VALUES (1, ?, ?, ?, ?, ?)
    """, (data.role, data.location, data.sectors, data.watching, data.sensitivity))
    conn.commit()
    conn.close()
    return {"status": "saved"}


# ── FEEDBACK ──────────────────────────────────────────────────────────────────

class FeedbackEvent(BaseModel):
    article_id: int
    action:     str


@app.post("/feedback")
def record_feedback(event: FeedbackEvent):
    if event.action not in ("click", "dismiss"):
        return {"status": "ignored"}
    conn = get_connection()
    conn.execute("INSERT INTO feedback (article_id, action) VALUES (?, ?)",
                 (event.article_id, event.action))
    conn.commit()
    conn.close()
    return {"status": "recorded"}


@app.get("/feedback/stats")
def feedback_stats():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.source, f.action, COUNT(*) as count
        FROM feedback f
        JOIN articles a ON f.article_id = a.id
        GROUP BY a.source, f.action
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── MANUAL TRIGGERS ───────────────────────────────────────────────────────────

@app.post("/ingest")
def trigger_ingest():
    from ingest import fetch_and_store
    fetch_and_store()
    return {"status": "done"}


@app.post("/score")
def trigger_score():
    from score import score_unscored_articles
    score_unscored_articles()
    return {"status": "done"}
