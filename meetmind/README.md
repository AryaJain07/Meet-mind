# 🧠 MeetMind — AI Meeting Notes & Summarizer

An AI-powered web application that automatically extracts insights from meeting transcripts using **FastAPI** backend and **Google Gemini API**.

---

## 📁 Project Structure

```
meetmind/
├── backend/
│   ├── main.py               ← FastAPI app entry point
│   ├── .env                  ← API keys (never commit this)
│   ├── database/
│   │   └── models.py         ← SQLAlchemy DB models
│   └── routes/
│       ├── analyze.py        ← POST /api/analyze
│       └── meetings.py       ← GET/DELETE /api/meetings
├── frontend/
│   └── index.html            ← Full frontend (HTML/CSS/JS)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python, FastAPI |
| Database | SQLite (via SQLAlchemy ORM) |
| AI Model | Google Gemini 1.5 Flash |
| Server | Uvicorn (ASGI) |

---

## 🚀 How to Run

### Step 1 — Clone & Setup

```bash
cd meetmind
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set API Key

Open `backend/.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_key_here
```
Get a free key at: https://aistudio.google.com

### Step 5 — Run Backend

```bash
cd backend
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000  
API Docs at: http://localhost:8000/docs

### Step 6 — Open Frontend

Open `frontend/index.html` directly in your browser.

---

## 📡 API Endpoints

### POST `/api/analyze`
Analyze a meeting transcript.

**Request:**
```json
{
  "transcript": "John: Let's discuss Q4...",
  "options": {
    "summary": true,
    "actions": true,
    "decisions": true,
    "sentiment": false,
    "participants": true
  }
}
```

**Response:**
```json
{
  "id": 1,
  "summary": "The team discussed Q4 targets...",
  "action_items": [
    { "task": "Prepare budget proposal", "owner": "Sarah", "priority": "high" }
  ],
  "key_points": ["Revenue is 12% behind target"],
  "participants": ["John", "Sarah"],
  "meeting_meta": {
    "meeting_type": "Strategy",
    "duration_estimate": "30 mins",
    "topic": "Q4 Planning"
  }
}
```

### GET `/api/meetings`
Get all past meetings from database.

### GET `/api/meetings/{id}`
Get a specific meeting by ID.

### DELETE `/api/meetings/{id}`
Delete a meeting from database.

---

## ✨ Features

- **AI Summarization** — 2-3 sentence executive summary
- **Action Item Extraction** — Who does what, with priority
- **Key Points** — Important decisions highlighted
- **Sentiment Analysis** — Positive/Neutral/Negative tone
- **Participant Detection** — Auto-detect attendees
- **Meeting History** — All meetings saved in SQLite database
- **Export** — Copy as Markdown or JSON
- **Sample Transcripts** — 4 built-in demo transcripts

---

## 🔒 Security Notes

- API key is stored in `.env` file (server-side only)
- `.env` is in `.gitignore` — never pushed to GitHub
- Frontend communicates with backend, never directly with Gemini

---

## 👨‍💻 Developer

Built as an internship project demonstrating:
- RESTful API design with FastAPI
- LLM integration for NLP tasks
- Database design with SQLAlchemy ORM
- Full-stack web development
