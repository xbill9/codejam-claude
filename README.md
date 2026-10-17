# ⚡ Resume Tailor

> **Instant, high-impact resume bullet transformer powered by Google Gemini and the Google XYZ framework.**

---

## What This App Does (In Plain English)

When applying for competitive jobs, generic resume bullets get overlooked. Tailoring bullets by hand to match each role's specific keywords and impact metrics is tedious and time-consuming.

**Resume Tailor** solves this with ruthless simplicity:
1. **Paste two things**: Your current resume bullets and the target job description.
2. **Click "Tailor Bullets"**: In ~3 seconds, Gemini analyzes the role's competencies and elevates each bullet into an executive-ready accomplishment following Google's XYZ formula:
   > *"Accomplished [X], as measured by [Y], by doing [Z]"*
3. **Compare & Copy**: Review a high-contrast side-by-side **Before → After Impact Diff** showing your original bullet next to the upgraded version, complete with highlighted action verbs, quantified metrics, and one-click copy buttons.

No file uploads, no login walls, no PDF glitches—just pure, high-leverage copy-paste upgrade.

---

## Design Docs as Source of Truth

This project was built strictly from three authoritative design documents. Anyone working on or extending this project should read them first:

1. **[`product.md`](product.md) — Product Design Doc (PRD)**
   - Defines the user, the trigger moment, the I/O contract, what we are building, and what we **deliberately chose NOT to build** (no PDF parsing, no user auth, no cover letters, no databases) to maintain extreme scope discipline.
2. **[`ui.md`](ui.md) — UX Design Doc**
   - Details the single-screen responsive workspace, the defining interaction, screen layout, loading and error states, visual typography, and accessibility standards.
3. **[`engineering.md`](engineering.md) — Engineering Design Doc**
   - Outlines the system architecture, Pydantic data schemas, API contracts (`POST /api/tailor`, `GET /api/health`), architectural trade-offs, and the automated testing strategy.

---

## Tech Stack

- **Backend**: Python 3.12+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **AI / LLM**: Official [`google-genai`](https://github.com/googleapis/python-genai) SDK with `gemini-3.8-flash`
- **Frontend**: Zero-dependency vanilla HTML5, modern CSS3, and ES6+ JavaScript (served directly by FastAPI static mount—no Node.js or bundlers needed)
- **Package & Runtime Manager**: [`uv`](https://docs.astral.sh/uv/)
- **Testing**: `pytest` and `httpx`

---

## Setup & Installation on a New Machine

### 1. Prerequisites
- **Git**: Installed on your system.
- **Python**: 3.11 or newer.
- **uv**: Astral's fast Python package manager. If not installed:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Clone the Repository
```bash
git clone https://github.com/gca-americas/codingjam-bulletproof.git resume-tailor
cd resume-tailor
```

### 3. Install Dependencies
Run `uv sync` from the project root to create a local virtual environment (`.venv`) and install all required packages:
```bash
uv sync
```

### 4. Configure Environment Variables
Copy `.env.example` to `backend/.env` (and optionally create a symlink to root `.env`):
```bash
cp .env.example backend/.env
```

Open `backend/.env` and insert your Gemini API key:
```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
PORT=8000
```

> **Note**: Both `backend/.env` and `.env` are listed in `.gitignore` to prevent credentials from ever being committed.

---

## Running the Application

### Start the Development Server
From the project root, run:
```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Web App**: Open **[http://localhost:8000](http://localhost:8000)** in your browser.
- **Health Check**: Visit **[http://localhost:8000/api/health](http://localhost:8000/api/health)** (`{"status": "ok", "model": "gemini-3.8-flash"}`).

---

## Running the Test Suite

Execute the automated test suite using `pytest` via `uv`:
```bash
uv run pytest -v
```

The test suite covers:
- **Unit Tests (`tests/test_unit.py`)**: Bullet point parsing (`-`, `*`, `•`, `1.`), whitespace stripping, `TailorRequest` boundary validation, prompt construction, and schema fallback handling.
- **Integration Tests (`tests/test_integration.py`)**: Mocked end-to-end `/api/tailor` transformation pipeline, `/api/health` status, upstream Gemini exception handling (500), and rate-limit handling (429).
