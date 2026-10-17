# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Resume Tailor: a 45-minute code-jam build. It is a FastAPI + `google-genai` backend, and FastAPI serves the vanilla HTML/CSS/JS frontend (no build step) from `frontend/` at `/`.

## Commands

Run everything from the repo root. Imports are `from backend...`, so the module is `backend.main` (engineering.md's `uvicorn main:app` is wrong for this layout).

- Install: `uv sync`
- Run: `uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- Tests: `uv run pytest -v`. Single test: `uv run pytest tests/test_unit.py::TestBulletExtraction::test_extract_dash_bullets`
- Lint/format: `ruff format` and `ruff check --fix` (not configured in pyproject; defaults apply)

## Environment

- Copy `.env.example` to `backend/.env`. `main.py` loads `backend/.env`, then the root `.env`.
- `GEMINI_API_KEY` is used if set. Otherwise the client falls back to Vertex AI via `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION`.
- `GEMINI_MODEL` (default `gemini-3.8-flash`) is read when `backend.generator` is imported, which happens before `load_dotenv` runs. A value set only in `.env` is ignored; it must be exported in the shell.

## Source of truth

- `product.md`, `engineering.md` and `ui.md` are the spec. Where they disagree with the code, bring the code in line with the docs. Known gaps:
  - Gemini should be called with `response_schema`; the code only sets `response_mime_type`.
  - The character counter needs an amber warning at 12,000 characters.
  - Validation errors should return 400; FastAPI currently returns 422.
  - Response field names differ between ui.md and the code.
- **Exception:** the model is `gemini-3.8-flash`. engineering.md's `gemini-2.5-flash` is outdated.
- `reference/moodjar-example/` is an earlier jam app that engineering.md cites as the pattern to follow (client setup, prompts in `prompts.py`, static mount). It is not part of this app.

## Scope: do not build

From BRIEF.md, product.md §5 and engineering.md §4/§8/§14:

- Text input only. No PDF/DOCX upload or parsing, cover letters, interview prep, Word export, or URL fetching/scraping.
- No auth, database, saved history, task queue or microservices.
- Don't install Node.js. Everything runs in one Python process with no bundlers.
- Banned dependencies: `pdfminer`, `pypdf`, `python-docx`, `beautifulsoup4`, `playwright`, `selenium`, Celery, Redis, JWT/OAuth libraries.
- UI (ui.md): a single screen with no sub-pages, tabs or modals, no settings or theme selector, light mode only. Errors render inline.

## Behavior constraints

- When the input has no numbers, use bracketed metric placeholders (e.g. `[by 25%]`) instead of invented figures (engineering.md §9).
- Latency target: under 4s for up to 8 bullets. Input is capped at 10 bullets.
- Validation limits are mirrored in `backend/models.py` and `frontend/app.js`. Change both together.
- Tests never call the live Gemini API. They mock `backend.generator.create_client`, and new tests should do the same.
