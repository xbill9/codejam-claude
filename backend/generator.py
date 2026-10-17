"""Gemini AI generation service for Resume Tailor."""

import json
import os
from typing import Optional

from google import genai
from google.genai import types

from backend.models import TailorResponse, TailoredBullet
from backend.prompts import SYSTEM_PROMPT, build_prompt, extract_raw_bullets

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def create_client():
    """Create a Gemini API client using API key or Google Cloud / Vertex AI auth."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )


def generate_tailored_bullets(
    job_description: str,
    resume_text: str,
    client: Optional[object] = None,
) -> TailorResponse:
    """Extract bullets, construct prompt, query Gemini, and return validated TailorResponse."""
    bullets = extract_raw_bullets(resume_text)
    if not bullets:
        raise ValueError("Could not extract any bullet points from the provided resume text.")

    # Limit to top 10 bullets to adhere to latency budget
    bullets = bullets[:10]

    user_prompt = build_prompt(job_description, bullets)

    ai_client = client or create_client()

    response = ai_client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=[
            {
                "role": "user",
                "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_prompt}],
            }
        ],
        config=types.GenerateContentConfig(
            temperature=0.4,
            response_mime_type="application/json",
        ),
    )

    response_text = response.text.strip() if hasattr(response, "text") and response.text else ""

    # Strip markdown code fences if model returned them despite response_mime_type
    if response_text.startswith("```"):
        lines = response_text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        response_text = "\n".join(lines).strip()

    data = json.loads(response_text)

    # Normalize data into TailorResponse
    if isinstance(data, list):
        data = {"bullets": data, "role_summary": "Tailored to job requirements"}

    parsed_bullets = []
    raw_bullets_list = data.get("bullets", [])
    for idx, item in enumerate(raw_bullets_list):
        if not isinstance(item, dict):
            continue
        orig = item.get("original") or (bullets[idx] if idx < len(bullets) else "Original bullet")
        tailored = item.get("tailored") or item.get("text") or orig
        action_verb = item.get("action_verb") or tailored.split()[0] if tailored.split() else "Implemented"
        key_skill = item.get("key_skill") or "Core Skill"
        impact_metric = item.get("impact_metric") or "Quantified Outcome"
        
        parsed_bullets.append(
            TailoredBullet(
                original=orig,
                tailored=tailored,
                action_verb=action_verb,
                key_skill=key_skill,
                impact_metric=impact_metric,
            )
        )

    return TailorResponse(
        role_summary=data.get("role_summary", "Tailored to job requirements"),
        bullets=parsed_bullets,
    )
