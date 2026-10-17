---
name: verify
description: Verify Resume Tailor changes end to end — ruff lint, the pytest suite, then boot the FastAPI app and hit /api/health and the frontend. Use after changing backend or frontend code, or before declaring a task done.
---

Run each step from the repo root. Stop at the first failure and report its output. Do not skip ahead.

1. **Lint:** `ruff check backend tests`
2. **Tests:** `uv run pytest -q`. If dependencies are missing, run `uv sync` first. The tests mock Gemini, so no API key is needed.
3. **Smoke test:** start the server in the background on a spare port so it doesn't collide with a dev server already running on 8000:
   ```
   uv run uvicorn backend.main:app --port 8765
   ```
   Wait for it to accept connections, then:
   - `curl -sf localhost:8765/api/health`. It should return `{"status":"ok","model":...}`, and the model should be `gemini-3.8-flash` unless `GEMINI_MODEL` is exported.
   - `curl -sf localhost:8765/ | grep -qi '<html'`. This confirms the frontend is being served.
   - Stop the server afterwards.
4. **Optional live call:** only if the user asks and `GEMINI_API_KEY` is set. POST a short job description and two resume bullets to `/api/tailor`, and check that the response matches the contract in engineering.md §7.

Report one line per step (pass or fail). For any failure, include the relevant output.
