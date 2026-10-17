"""Resume Tailor — FastAPI application server."""

import os
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.generator import DEFAULT_MODEL, generate_tailored_bullets
from backend.models import TailorRequest, TailorResponse

# Explicitly load .env from backend folder, falling back to root .env
_backend_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_backend_dir, ".env"))
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify GEMINI_API_KEY is present and SDK is ready at startup."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        masked = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
        print(f"INFO:     GEMINI_API_KEY detected at startup ({masked})")
    else:
        print("WARNING:  GEMINI_API_KEY not found in environment at startup")
    yield


app = FastAPI(
    title="Resume Tailor",
    description="Instant high-impact Google XYZ resume bullet transformer",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for local testing and flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "model": DEFAULT_MODEL}


@app.post("/api/tailor", response_model=TailorResponse)
async def tailor_bullets(request: TailorRequest):
    """Transform raw job text and candidate bullets into Google XYZ tailored accomplishments."""
    try:
        response = generate_tailored_bullets(
            job_description=request.job_description,
            resume_text=request.resume_text,
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="The model generated an unparseable response format. Please retry.",
        )
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit reached. Please wait a moment and try again.",
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate tailored bullets: {error_msg}",
        )


# Mount frontend static assets if directory exists
frontend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
