# Resume Tailor — Engineering Design Doc

**Author:** TBD  
**Status:** Draft v0.1  
**Last updated:** 2026-10-16  
**Reviewers:** TBD  

---

## 1. Summary

Resume Tailor is a single-service web application that transforms raw user resume bullets and job postings into executive-ready Google XYZ accomplishments (*"Accomplished [X], as measured by [Y], by doing [Z]"*). The architecture follows a lightweight, unified Python monolith: a FastAPI backend powered by the official `google-genai` SDK using Gemini Flash, which concurrently serves a zero-dependency vanilla HTML/CSS/JavaScript single-page frontend. The primary engineering decision is enforcing structured JSON generation via Gemini with strict Pydantic schemas, eliminating brittle markdown parsing and allowing deterministic, side-by-side Before/After card rendering under a strict 4-second latency ceiling.

## 2. Assumptions

- **Target scale:** <5,000 requests/day in v1 (single-node capacity).
- **Latency budget:** End-to-end p95 < 4.0s from user button click to DOM card render.
- **Platform:** Modern desktop and mobile web browsers (Chrome, Safari, Firefox, Edge).
- **Runtime environment:** Python 3.11+ managed via `uv`, with zero Node.js/npm dependencies.
- **Cost ceiling:** <$0.005 per tailoring session using Gemini 2.5 Flash tokens.
- **Out of scope:** User authentication, persistent databases, document parsing (PDF/DOCX), multi-region clustering.

## 3. Goals & non-goals

**Goals (v1):**
- Accept raw text for job description and 1–10 resume bullet points via a clean web interface.
- Deconstruct and align each bullet to the target role's competencies and rewrite it according to the Google XYZ framework.
- Return structured pairs containing original bullet, tailored bullet, action verb, and primary targeted skill.
- Maintain end-to-end latency p95 < 4.0s (model generation latency < 3.0s).
- Run completely self-contained from a single executable process (`uv run uvicorn main:app`).

**Non-goals (v1):**
- No user accounts, sessions, or cloud databases. All operations are stateless in-memory requests.
- No file parsing for binary resume files (.pdf, .docx, .rtf).
- No web scraping or live URL fetching of job boards.
- No cover letter or multi-page resume compilation.
- Scale target is strictly single-instance; no distributed microservices, message queues, or Celery workers.

## 4. Architecture

```mermaid
flowchart LR
    Browser[Single-Page Client\nVanilla HTML5 / CSS / JS] -->|POST /api/tailor\n(Job Text + Bullets)| Server[FastAPI Server\nUvicorn :8000]
    Server -->|Static Files\nMount /| Browser
    Server -->|Structured Schema Prompt| Gemini[Gemini 2.5 Flash\ngoogle-genai SDK]
    Gemini -->|Validated JSON Array| Server
    Server -->|HTTP 200 JSON Response| Browser
```

**What's here:**
- **FastAPI / Uvicorn Server:** Handles HTTP routing, input validation via Pydantic, and serves static frontend assets directly.
- **Gemini AI Client:** Integrates with `google-genai` using `gemini-2.5-flash`, structured schema output (`application/json`), and prompt templates.
- **Vanilla Web Client:** Lightweight HTML5, CSS3, and modern JavaScript app that handles input validation, API calls, state transitions, and clipboard operations.

**What's deliberately NOT here:**
- **No Node.js / Webpack / Vite build pipeline:** The frontend uses standard browser features without a compiler or bundler step, eliminating JavaScript toolchain friction.
- **No database or ORM (PostgreSQL, SQLite, Redis):** Requests are stateless and processed immediately; no persistence layer is required.
- **No asynchronous task queue (Celery, Redis Queue):** Requests complete synchronously within HTTP timeout limits (<5s), avoiding worker daemon overhead.
- **No multi-stage proxy or microservices:** A single Python process serves both the REST API and the static web assets.

## 5. Key components

### FastAPI Application Server (`backend/main.py`)
- **Responsibility:** Validates incoming payloads, invokes the prompt pipeline, manages API errors, and serves static frontend files.
- **Tech choice:** Python 3.12, FastAPI, Uvicorn.
- **Why this choice:** As demonstrated in `reference/moodjar-example`, FastAPI provides high-speed ASGI performance, native Pydantic schema validation, and simple static file mounting without external web servers.
- **Interface:** Exposes `POST /api/tailor` and `GET /api/health`.

### Gemini Inference Service (`backend/generator.py` & `backend/prompts.py`)
- **Responsibility:** Formats input into specialized prompt instructions and calls the Gemini API requesting structured JSON output.
- **Tech choice:** Official `google-genai` Python SDK (`from google import genai`).
- **Why this choice:** Standardizes on Google's current GenAI SDK with native support for `response_mime_type="application/json"` and `response_schema`.
- **Interface:** `tailor_resume_bullets(job_description: str, bullets: list[str]) -> list[TailoredBulletPair]`.

### Frontend Studio UI (`frontend/app.js`, `frontend/index.html`, `frontend/style.css`)
- **Responsibility:** Manages the dual input forms, client-side character count validation, API interaction, loading states, and clipboard copy operations.
- **Tech choice:** Vanilla HTML5, modern CSS with flex/grid, ES6+ JavaScript.
- **Why this choice:** Zero npm/Node install footprint, instant local loading, and effortless maintainability with zero build dependencies.
- **Interface:** Consumes `/api/tailor` JSON response and renders DOM nodes.

## 6. Data model

### Python / Pydantic Schemas (`backend/models.py`)

```python
from pydantic import BaseModel, Field

class TailorRequest(BaseModel):
    job_description: str = Field(..., min_length=20, max_length=15000, description="Target job posting text")
    resume_text: str = Field(..., min_length=10, max_length=15000, description="Raw resume text or bullet points")

class TailoredBullet(BaseModel):
    original: str = Field(..., description="Original raw bullet point from candidate")
    tailored: str = Field(..., description="Upgraded bullet following Google XYZ format")
    action_verb: str = Field(..., description="High-impact lead action verb used (e.g., Spearheaded, Engineered)")
    key_skill: str = Field(..., description="Primary competency or keyword aligned to the job")
    impact_metric: str = Field(..., description="Quantifiable impact or outcome framing (e.g., 'reduced latency by 40%')")

class TailorResponse(BaseModel):
    bullets: list[TailoredBullet] = Field(..., description="List of transformed bullet point pairs")
    role_summary: str = Field(..., description="1-sentence takeaway of the primary role requirements")
```

### TypeScript / Client Data Model

```typescript
type TailoredBullet = {
  original: string;
  tailored: string;
  action_verb: string;
  key_skill: string;
  impact_metric: string;
};

type TailorResponse = {
  bullets: TailoredBullet[];
  role_summary: string;
};
```

## 7. API surface

### `POST /api/tailor`

- **Description:** Takes raw job text and resume bullets, parses and transforms bullets into XYZ format, and returns structured comparison pairs.
- **Input:**
  ```json
  {
    "job_description": "We are looking for a Senior Backend Engineer proficient in Python, FastAPI, and PostgreSQL...",
    "resume_text": "- Built backend APIs for auth\n- Managed database migrations\n- Improved query performance"
  }
  ```
- **Output:**
  ```json
  {
    "role_summary": "Senior Backend Engineer focusing on Python API reliability and database scalability",
    "bullets": [
      {
        "original": "Built backend APIs for auth",
        "tailored": "Architected and deployed OAuth2 authentication service in FastAPI across 14 microservices, reducing unauthorized login attempts by 32% while sustaining sub-40ms latency.",
        "action_verb": "Architected",
        "key_skill": "FastAPI Authentication",
        "impact_metric": "reduced unauthorized attempts by 32%"
      }
    ]
  }
  ```
- **Errors:**
  - `400 Bad Request`: Payload validation error (inputs empty or exceeding character limits).
  - `429 Too Many Requests`: Upstream Gemini rate limit encountered.
  - `500 Internal Server Error`: Upstream model failure or unparseable response.
- **Latency budget:** End-to-end p95 < 4.0s (3.0s model call + 0.3s network/FastAPI + 0.2s DOM render).

### `GET /api/health`

- **Output:** `{"status": "ok", "model": "gemini-2.5-flash"}`
- **Latency budget:** < 20ms.

## 8. Key trade-offs (with rejected alternatives)

### Decision: Python Monolith (FastAPI + Static Files) vs. Node.js/React Frontend + Python API
- **Chose:** Single Python monolith with FastAPI mounting vanilla frontend static assets.
- **Considered:** Separate React/Next.js frontend with Node build scripts and separate Python FastAPI backend.
- **Why we picked this:** The user explicitly directed: *"Don't install Node.js."* A single Python process managed by `uv` runs everything with zero external runtimes or build steps, avoiding port collisions and CORS configurations.

### Decision: Native Structured JSON Output vs. Freeform Markdown with Regex Extraction
- **Chose:** Gemini API native JSON schema enforcement (`response_mime_type="application/json"` with Pydantic).
- **Considered:** Prompting for markdown bullets and parsing with regular expressions on the server.
- **Why we picked this:** LLMs frequently produce unexpected markdown tokens (varying asterisks, dash styles, missing headers). Strict schema validation guarantees exact object shapes for the side-by-side frontend diff cards with zero regex parsing bugs.

### Decision: Synchronous Single-Shot Generation vs. Chunked/Streaming Bullets
- **Chose:** Synchronous single-shot generation of the complete bullet list.
- **Considered:** Server-Sent Events (SSE) streaming individual bullet points.
- **Why we picked this:** Gemini 2.5 Flash processes up to 8 bullets in ~2.0 seconds. Streaming adds client state machine complexity and SSE connection failure modes that are unnecessary for a 2-3s batch response.

## 9. Risks & unknowns

- **Upstream Gemini API Rate Limits (429):** Likelihood: Medium. Mitigation: Handle HTTP 429 gracefully with an exponential backoff retry (up to 2 retries) and deliver a friendly client-side retry notice if quota is exhausted.
- **Hallucinated Specific Metrics:** Likelihood: Medium. When an original user bullet lacks quantifiable numbers, the model may fabricate figures. Mitigation: System prompt explicitly instructs the model to use realistic metric bracket placeholders (e.g. `[by 25%]` or `[by ~30ms]`) when the raw input contains no numbers, signaling to the candidate to insert their true metric.
- **Clipboard API Browser Restrictions:** Likelihood: Low. Mitigation: Wrap `navigator.clipboard.writeText()` in a try/catch block with fallback to `document.execCommand('copy')` if clipboard permissions are blocked.

## 10. Testing strategy

This section defines the test plan to ensure rock-solid stability and rapid automated verification.

### Unit tests (`tests/test_unit.py`)
1. **Bullet Extraction (`extract_raw_bullets`):**
   - Verify that raw text containing dash bullets (`- `), asterisks (`* `), numbered lists (`1. `), or raw newlines is correctly sanitized into a discrete list of individual bullet strings.
   - Verify that empty lines, excessive whitespace, and non-bullet fluff are stripped.
2. **Request Validation (`TailorRequest`):**
   - Verify that requests with empty strings or whitespace-only fields raise `ValidationError`.
   - Verify that inputs exceeding 15,000 characters trigger 422 Unprocessable Entity.
3. **Structured Prompt Construction (`build_prompt`):**
   - Verify that the generated prompt injects both the job description and each extracted bullet cleanly into the system template with XYZ guidance.
4. **Response Validation (`TailoredBullet` / `TailorResponse`):**
   - Verify that valid JSON conforming to the schema parses cleanly into Pydantic models.
   - Verify default fallback behavior when optional fields are empty.

### Integration tests (`tests/test_integration.py`)
1. **Major Flow: Happy Path Tailoring (`test_tailor_flow_mocked`):**
   - Flow: POST valid `job_description` and `resume_text` to `/api/tailor`.
   - Setup: Mock the Gemini API client response with realistic structured JSON.
   - Assert: Returns HTTP 200, content-type `application/json`, payload contains matched pairs with `original`, `tailored`, and `action_verb` fields populated.
2. **Major Flow: Health Check (`test_health_endpoint`):**
   - Flow: GET `/api/health`.
   - Assert: Returns HTTP 200 and `{"status": "ok"}`.
3. **Major Flow: Upstream Failure Handling (`test_upstream_error_handling`):**
   - Flow: POST to `/api/tailor` when Gemini client raises an API error (e.g., 503 or timeout).
   - Assert: Returns HTTP 502/500 with a structured `{ "detail": "..." }` message without crashing the server.

### Deliberately NOT tested (and why)
- **Live Gemini API Calls in CI:** Real API calls require active credentials and incur costs and network flakiness. Mock responses are used for test suites.
- **Browser DOM rendering & CSS visual styling:** Visual layout and CSS flex/grid rendering are verified manually; headless browser test frameworks (Playwright/Cypress) are out of scope for v1.
- **Clipboard execution:** `navigator.clipboard` behavior depends on browser-level OS security sandboxes and is omitted from automated test suites.

### Stack defaults
- Test Runner: `pytest`
- API Testing Client: `httpx` (FastAPI `TestClient`)
- Test directory: `tests/`
- Command: `uv run pytest`

## 11. Rollout & monitoring

- **Deployment:** Single container or host run via `uv run uvicorn main:app --host 0.0.0.0 --port 8000`.
- **Environment Configuration:**
  - `GEMINI_API_KEY`: API key for Google Gemini.
  - `PORT`: Server port (default: 8000).
- **Monitoring Signals:**
  - HTTP 5xx error rate on `/api/tailor`.
  - p95 and p99 latency on the `/api/tailor` endpoint.
  - Count of Gemini API rate-limit errors (429).
- **Rollback plan:** Graceful restart to previous Git commit or process restart via process supervisor (`systemd` / container orchestrator).

## 12. Cost & capacity

- **Model:** `gemini-2.5-flash`.
- **Token consumption per call:**
  - Input: ~1,500 tokens (System prompt: 500 tokens, Job description: 700 tokens, Bullets: 300 tokens).
  - Output: ~400 tokens (Structured JSON for 5 bullets).
- **Cost per call:** ~$0.0003 per session.
- **Monthly cost at 10,000 monthly requests:** ~$3.00 total LLM expenditure.
- **10× scale bottleneck:** API concurrency rate limits on Gemini Flash tier; mitigated by moving to pay-as-you-go quota or caching repeated job description embeddings.

## 13. Open questions

- [ ] What is the optimal temperature setting (e.g. 0.3 vs 0.7) to maximize punchy XYZ phrasing while preventing hallucinated job responsibilities? (Owner: Eng Lead)
- [ ] Should the server trim input job postings greater than 5,000 characters to optimize token spend? (Owner: Backend Eng)

## 14. Out of scope (will not do)

- **No Database / Cache Layer:** No PostgreSQL, Redis, or DynamoDB.
- **No Background Workers:** No Celery, RQ, or RabbitMQ.
- **No User Auth / Accounts:** No JWTs, OAuth2, session cookies, or user tables.
- **No File Parsers:** No `pdfminer`, `pypdf`, or `python-docx` dependencies.
- **No Web Scrapers:** No `beautifulsoup4`, `playwright`, or `selenium`.
