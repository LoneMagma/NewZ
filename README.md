<div align="center">

# NewZ

### News, filtered without the noise.

**Try it:** https://newz.pacify.site  
*Built on* **pacify.site**

<!-- Demo animation (replace the URL with your hosted GIF/MP4) -->
<img src="https://newz.pacify.site/demo.gif" alt="NewZ demo animation" width="900" />

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-f55036?style=flat-square)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

</div>

---

## What it is

**NewZ** is a self-hosted news aggregator that turns raw RSS into a **ranked feed** for each user.

**v3** is built around a clean separation:

- **Server**: reads articles and extracts *what the article is about* (topics, entities, urgency)
- **Client**: decides *what matters to a specific user* (personalization + ranking)

This makes the system correct for **multi-user** setups and keeps personalization logic close to the UI.

---

## What changed in v3.0 (concrete)

### 1) Architecture shift: extraction, not “relevance-to-you”
The LLM no longer scores “how relevant is this to you.”  
It now extracts:

- `key_topics` — normalized topic tags
- `named_entities` — people/orgs/places
- `urgency_score` — breaking-ness / time-sensitivity signal

**Personalization happens entirely on the client.**

### 2) Synonym explosion removed
`expandWithSynonyms` and `DOMAIN_SYNONYMS` are gone.

Matching is now **exact** against the server’s extracted tags.  
So `"War, Defence"` doesn’t balloon into dozens of unrelated terms.

### 3) Matching surface tripled
Client matches against:

- **title**
- **key_topics**
- **named_entities**

So an article like *“Iran threatens Hormuz”* can be matched via extracted tags like
`"geopolitical conflict", "sanctions"` and entities like `"Iran", "US Navy"`.

### 4) Role field now contributes (weak signal)
A role like `"Army officer"` maps to a small topic set such as:

`['military', 'defence', 'armed forces', 'strategic']`

It nudges adjacent matches **without overriding** clear non-matches.

### 5) Score spread: real ranking
Scores now spread roughly **2–9** (previously ~5–7), so the feed is actually ranked instead of compressed.

### 6) Sources expanded
Now **25 feeds** across:

- General Indian news (e.g., The Hindu, Indian Express)
- Indian tech (e.g., Inc42, YourStory)
- Indian official (e.g., RBI)
- Global health (e.g., STAT News, Nature)
- Global energy (e.g., Energy Monitor)
- Global analysis (e.g., Foreign Affairs)

---

## How it works

```text
RSS Feeds (25 sources)
      ↓
Ingestion (every 5 min)
      ↓
LLM Extraction (Groq · LLaMA 3.1)
  - key_topics
  - named_entities
  - urgency_score
      ↓
SQLite DB
      ↓
FastAPI Server (API)
      ↓
Client (personalize + rank)
```

### Schedulers
- Every **5 minutes**: fetch new articles, store metadata, mark “breaking” candidates
- Every **30 minutes**: run extraction for any unprocessed articles

---

## Data model (server output)

A typical extracted payload:

```json
{
  "key_topics": ["geopolitical conflict", "sanctions", "shipping"],
  "named_entities": ["Iran", "US Navy", "Strait of Hormuz"],
  "urgency_score": 8
}
```

The client combines these with the user’s interests to compute a final score and ordering.

---

## Project structure

```text
newz/
├── backend/
│   ├── main.py            FastAPI server + API routes
│   ├── ingest.py          RSS fetching and storage
│   ├── score.py           LLM extraction (topics/entities/urgency)
│   ├── scheduler.py       Two-tier background scheduler
│   ├── database.py        SQLite connection and schema
│   ├── config.py          Keys, feed URLs, paths
│   ├── setup_profile.py   One-time profile initialization
│   └── reset_scores.py    Dev utility — reset all extracted fields
├── frontend/
│   └── index.html         Single-page frontend
├── requirements.txt
├── .env                   ← not committed
└── .gitignore
```

---

## API

| Method | Endpoint               | Description                                  |
|--------|------------------------|----------------------------------------------|
| GET    | `/`                    | Frontend                                     |
| GET    | `/articles`            | Ranked articles (client-scored)              |
| GET    | `/articles/breaking`   | High urgency articles in last 2 hours        |
| GET    | `/articles/all`        | All articles (unfiltered)                    |
| GET    | `/profile`             | Current user profile                         |
| POST   | `/profile`             | Update user profile                          |
| POST   | `/ingest`              | Trigger manual ingest                        |
| POST   | `/score`               | Trigger manual extraction run                |

> Note: In v3, `/score` runs **extraction** (topics/entities/urgency).  
> Final personalization happens on the client.

---

## Sources (v3)

NewZ ships with **25 RSS feeds** across these buckets:

- **India (general)**: The Hindu, Indian Express, …
- **India (tech/startups)**: Inc42, YourStory, …
- **India (official)**: RBI, …
- **Global (health/science)**: STAT, Nature, …
- **Global (energy/climate)**: Energy Monitor, …
- **Global (analysis)**: Foreign Affairs, …

To customize feeds, edit the feed list in `backend/config.py`.

---

## License

MIT — see `LICENSE`.

---

<div align="center">

Made by **LoneMagma** · Built on **pacify.site**

</div>
