<div align="center">

# NewZ

**News. Filtered for you.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-f55036?style=flat-square)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-MVP-f59e0b?style=flat-square)]()

*Built on [pacify.site](https://pacify.site)*

</div>

---

## What it is

NewZ is a self-hosted financial news aggregator that uses an LLM to score every article against your personal profile — your sector interests, location, and what you're actively watching. Noise stays out. Signal comes through.

Powered by **Pacify** — a quiet AI layer that reads your feed and surfaces what matters.

---

## How it works

```
RSS Feeds (5 sources)
      ↓
  Ingestion        every 5 min
      ↓
 LLM Scoring       Groq · LLaMA 3.1
      ↓
  SQLite DB
      ↓
 FastAPI Server
      ↓
  Frontend         localhost:8000
```

**Two-tier scheduler:**
- Every **5 minutes** — fetch new articles, flag breaking news by keyword
- Every **30 minutes** — score all unscored articles against your profile

---

## Stack

| Layer       | Tech                        |
|-------------|-----------------------------|
| Backend     | Python · FastAPI · Uvicorn  |
| AI Scoring  | Groq API · LLaMA 3.1 8B     |
| Database    | SQLite                      |
| Ingestion   | feedparser · RSS            |
| Frontend    | Vanilla HTML/CSS/JS         |
| Scheduler   | Python threading            |

---

## Setup

**1. Clone and install**
```bash
git clone https://github.com/yourusername/newz.git
cd newz
pip install -r requirements.txt
```

**2. Add your Groq API key**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

**3. Set up your profile**
```bash
cd backend
python setup_profile.py
```

**4. Run the first ingest + score**
```bash
python ingest.py
python score.py
```

**5. Start the server**
```bash
python -m uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000)

---

## Project structure

```
newz/
├── backend/
│   ├── main.py            FastAPI server + API routes
│   ├── ingest.py          RSS fetching and storage
│   ├── score.py           LLM relevance scoring
│   ├── scheduler.py       Two-tier background scheduler
│   ├── database.py        SQLite connection and schema
│   ├── config.py          Keys, feed URLs, paths
│   ├── setup_profile.py   One-time profile initialisation
│   └── reset_scores.py    Dev utility — reset all scores
├── frontend/
│   └── index.html         Single-page frontend
├── requirements.txt
├── .env                   ← not committed
└── .gitignore
```

---

## API

| Method | Endpoint           | Description                        |
|--------|--------------------|------------------------------------|
| GET    | `/`                | Frontend                           |
| GET    | `/articles`        | Scored articles (default min: 5)   |
| GET    | `/articles/breaking` | High-score articles last 2 hrs   |
| GET    | `/articles/all`    | All articles unfiltered            |
| GET    | `/profile`         | Current user profile               |
| POST   | `/profile`         | Update user profile                |
| POST   | `/ingest`          | Trigger manual ingest              |
| POST   | `/score`           | Trigger manual score run           |

---

## News sources

| Source           | Region |
|------------------|--------|
| ET Markets       | 🇮🇳 India  |
| Mint Markets     | 🇮🇳 India  |
| Moneycontrol     | 🇮🇳 India  |
| Reuters Business | 🌐 Global |
| BBC Business     | 🌐 Global |

---

<div align="center">

Made by [Aryan](https://pacify.site) · Not financial advice

</div>
