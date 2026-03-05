import os
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(f"GROQ_API_KEY not found. Looked for .env at: {_env_path}")

RSS_FEEDS = [
    # ── INDIAN GENERAL / POLITICAL ────────────────────────────────────────
    {"name": "The Hindu",          "url": "https://www.thehindu.com/feeder/default.rss",                              "region": "IN", "tier": 2},
    {"name": "Indian Express",     "url": "https://indianexpress.com/feed/",                                          "region": "IN", "tier": 2},
    {"name": "NDTV",               "url": "https://feeds.feedburner.com/ndtvnews-top-stories",                        "region": "IN", "tier": 2},

    # ── INDIAN FINANCIAL ──────────────────────────────────────────────────
    {"name": "ET Markets",         "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",     "region": "IN", "tier": 2},
    {"name": "ET Economy",         "url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms","region": "IN", "tier": 2},
    {"name": "Mint",               "url": "https://www.livemint.com/rss/news",                                        "region": "IN", "tier": 2},
    {"name": "Moneycontrol",       "url": "https://www.moneycontrol.com/rss/MCtopnews.xml",                           "region": "IN", "tier": 2},
    {"name": "Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/feeder/default.rss",                  "region": "IN", "tier": 2},
    {"name": "NDTV Profit",        "url": "https://feeds.feedburner.com/ndtvprofit-latest",                           "region": "IN", "tier": 2},

    # ── INDIAN OFFICIAL / POLICY ──────────────────────────────────────────
    {"name": "PIB India",          "url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",                   "region": "IN", "tier": 1},
    {"name": "RBI",                "url": "https://www.rbi.org.in/Scripts/RSSFeedsRoot.aspx?Id=2",                    "region": "IN", "tier": 1},

    # ── INDIAN TECH / STARTUP ─────────────────────────────────────────────
    {"name": "Inc42",              "url": "https://inc42.com/feed/",                                                  "region": "IN", "tier": 2},
    {"name": "YourStory",          "url": "https://yourstory.com/feed",                                               "region": "IN", "tier": 2},

    # ── GLOBAL NEWS ───────────────────────────────────────────────────────
    {"name": "BBC World",          "url": "https://feeds.bbci.co.uk/news/world/rss.xml",                              "region": "GLOBAL", "tier": 2},
    {"name": "BBC Business",       "url": "https://feeds.bbci.co.uk/news/business/rss.xml",                           "region": "GLOBAL", "tier": 2},
    {"name": "Al Jazeera",         "url": "https://www.aljazeera.com/xml/rss/all.xml",                                "region": "GLOBAL", "tier": 2},
    {"name": "Reuters",            "url": "https://feeds.reuters.com/reuters/topNews",                                 "region": "GLOBAL", "tier": 2},

    # ── GLOBAL ANALYSIS ───────────────────────────────────────────────────
    {"name": "The Economist",      "url": "https://www.economist.com/finance-and-economics/rss.xml",                  "region": "GLOBAL", "tier": 3},
    {"name": "Foreign Affairs",    "url": "https://www.foreignaffairs.com/rss.xml",                                   "region": "GLOBAL", "tier": 3},

    # ── GLOBAL TECH ───────────────────────────────────────────────────────
    {"name": "TechCrunch",         "url": "https://techcrunch.com/feed/",                                             "region": "GLOBAL", "tier": 3},
    {"name": "MIT Tech Review",    "url": "https://www.technologyreview.com/feed/",                                   "region": "GLOBAL", "tier": 3},
    {"name": "Ars Technica",       "url": "https://feeds.arstechnica.com/arstechnica/index",                          "region": "GLOBAL", "tier": 3},

    # ── GLOBAL HEALTH / SCIENCE ───────────────────────────────────────────
    {"name": "Nature News",        "url": "https://www.nature.com/nature.rss",                                        "region": "GLOBAL", "tier": 3},
    {"name": "STAT News",          "url": "https://www.statnews.com/feed/",                                           "region": "GLOBAL", "tier": 3},

    # ── GLOBAL ENERGY / CLIMATE ───────────────────────────────────────────
    {"name": "Energy Monitor",     "url": "https://www.energymonitor.ai/feed/",                                       "region": "GLOBAL", "tier": 3},
]

TIER_MULTIPLIERS = {1: 1.30, 2: 1.0, 3: 0.85}

RECENCY_DECAY = [
    (1,   1.0),
    (3,   0.95),
    (6,   0.88),
    (12,  0.78),
    (24,  0.65),
    (48,  0.50),
    (999, 0.35),
]

NOISE_PATTERNS = [
    "horoscope", "astrology", "zodiac",
    "crossword", "sudoku", "quiz",
    "recipe ", "cooking tip",
    "box office", "film review", "movie review", "album review",
    "ipl match", "t20 match", "test match", "odi match",
    "cricket score", "football score", "match preview", "match report",
    "weather forecast", "weather update",
    "obituary", "in memoriam",
    "photo gallery", "in pictures",
]

DB_PATH = os.getenv("NEWZ_DB_PATH") or str(Path(__file__).resolve().parent / "newz.db")
