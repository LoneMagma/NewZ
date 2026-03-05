"""
v1.1 scoring architecture
─────────────────────────
The LLM no longer scores relevance against a profile (which fails
on a shared/multi-user deployment). Instead it does three things:

1. Extracts key_topics  — what this article is actually about
2. Extracts named_entities — people, organisations, places, policies
3. Scores urgency_score — how time-sensitive (profile-agnostic)

The client uses key_topics + named_entities + title to match against
the user's local profile. Sector and geo scoring is done entirely
client-side. The LLM's job is understanding; the client's job is matching.
"""

import json
import time
from datetime import datetime, timezone
from groq import Groq
from config import GROQ_API_KEY, TIER_MULTIPLIERS, RECENCY_DECAY, NOISE_PATTERNS
from database import get_connection

client = Groq(api_key=GROQ_API_KEY)

CALL_INTERVAL = 1.2
MAX_RETRIES   = 3
RETRY_WAIT    = 6


def should_drop(title: str) -> bool:
    t = title.lower()
    return any(p in t for p in NOISE_PATTERNS)


def get_recency_multiplier(published_at: str) -> float:
    try:
        from dateutil import parser as dp
        pub = dp.parse(published_at)
        if pub and pub.tzinfo:
            age_hours = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
            for threshold, mult in RECENCY_DECAY:
                if age_hours <= threshold:
                    return mult
        return 1.0
    except Exception:
        return 1.0


def call_llm(prompt: str) -> dict:
    for attempt in range(MAX_RETRIES):
        try:
            resp    = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            content = resp.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content.strip())
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate_limit" in msg.lower():
                wait = RETRY_WAIT * (attempt + 1)
                print(f"    Rate limited — retrying in {wait}s ({attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                raise
    raise Exception(f"LLM call failed after {MAX_RETRIES} attempts")


def extract_article_intelligence(title: str, raw_text: str) -> dict:
    """
    Profile-agnostic extraction. Returns what the article IS about,
    not how relevant it is to anyone in particular.
    """
    prompt = f"""Analyse this news article and extract structured information.

Title: {title}
Excerpt: {raw_text[:600] if raw_text else 'No excerpt available'}

Extract the following. Be concise and specific.

key_topics: 4-8 comma-separated topic tags describing what this article covers.
  Use specific terms, not vague ones. Prefer: "interest rate", "military procurement",
  "pharmaceutical regulation", "bilateral trade" over "economy", "defence", "health", "trade".
  Include the specific domain, the specific action/event, and the geographic scope if relevant.

named_entities: comma-separated list of specific names mentioned — people, organisations,
  companies, policies, treaties, places. Max 8. Only include if clearly present.
  Examples: "Rajnath Singh, DRDO, Line of Control, RBI, Repo Rate, SEBI, Llama 3"

urgency_score: integer 1-10.
  10 = breaking event requiring immediate attention (market crash, war declaration, rate change)
  7  = significant development with near-term consequences
  5  = important context, not time-critical
  3  = analysis, background, or trend piece
  1  = evergreen content, historical, or low-stakes

summary: one factual sentence describing what happened or what this article reports.
  Do NOT say "this article discusses". Say what happened. Max 20 words.

Respond ONLY with valid JSON:
{{"key_topics": "...", "named_entities": "...", "urgency_score": 5, "summary": "..."}}"""

    return call_llm(prompt)


def score_unscored_articles():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, raw_text, tier, published_at
        FROM articles
        WHERE relevance_score = 0
    """)
    articles = cursor.fetchall()

    # pre-filter — no API call needed
    to_score, dropped = [], 0
    for a in articles:
        if should_drop(a["title"]):
            cursor.execute("UPDATE articles SET relevance_score = -1 WHERE id = ?", (a["id"],))
            dropped += 1
        else:
            to_score.append(a)
    conn.commit()

    print(f"Scoring {len(to_score)} articles ({dropped} dropped by pre-filter)...")

    for article in to_score:
        try:
            result = extract_article_intelligence(
                article["title"],
                article["raw_text"] or ""
            )

            urgency     = max(1, min(10, int(result.get("urgency_score", 5))))
            key_topics  = result.get("key_topics",    "")
            entities    = result.get("named_entities", "")
            summary     = result.get("summary",        "")

            # relevance_score at ingest = urgency only (profile-agnostic)
            # Client re-ranks with full personalisation
            recency_mult = get_recency_multiplier(article["published_at"] or "")
            tier_mult    = TIER_MULTIPLIERS.get(article["tier"] or 2, 1.0)
            stored_score = max(1, min(10, round(urgency * recency_mult * tier_mult)))

            cursor.execute("""
                UPDATE articles
                SET relevance_score  = ?,
                    relevance_reason = ?,
                    urgency_score    = ?,
                    sector_score     = 0,
                    geo_score        = 0,
                    key_topics       = ?,
                    named_entities   = ?
                WHERE id = ?
            """, (stored_score, summary, urgency, key_topics, entities, article["id"]))
            conn.commit()

            print(f"  [U:{urgency}] {article['title'][:60]}")
            print(f"    topics: {key_topics[:80]}")
            if entities:
                print(f"    entities: {entities[:60]}")

            time.sleep(CALL_INTERVAL)

        except Exception as e:
            print(f"  Error on '{article['title'][:50]}': {e}")

    conn.close()
    print("Scoring complete.")


if __name__ == "__main__":
    score_unscored_articles()
