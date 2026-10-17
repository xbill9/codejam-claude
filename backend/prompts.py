"""Prompt templates and bullet parsing utilities for Resume Tailor."""

import re
from typing import List

SYSTEM_PROMPT = """You are an elite executive resume writer and career coach specializing in the Google XYZ resume bullet framework:
"Accomplished [X], as measured by [Y], by doing [Z]"

Your task is to take a target Job Description and a list of Candidate Resume Bullets, and elevate each bullet point into a high-impact, executive-ready accomplishment directly aligned with the target role.

RULES FOR REWRITING:
1. Every tailored bullet MUST follow the Google XYZ formula: Start with a punchy past-tense action verb (e.g., Architected, Spearheaded, Accelerated, Optimized), specify the measured business/technical outcome [Y], and explain the technical or strategic method [Z].
2. Align explicitly with key competencies, tools, and methodologies mentioned in the target Job Description.
3. If an original bullet lacks quantifiable numbers, provide realistic outcome brackets such as [by 25%], [reducing latency by ~30ms], or [saving $15k/mo] so the user can easily calibrate their authentic number.
4. Keep the bullet grounded in the candidate's actual original scope — do not hallucinate unrelated skills or leadership titles that the candidate never claimed.
5. Return ONLY a valid JSON object matching the requested schema. No markdown wrapping, no extra prose.

SCHEMA FORMAT:
{
  "role_summary": "1-sentence summary of the target role focus",
  "bullets": [
    {
      "original": "Original raw bullet text",
      "tailored": "Upgraded XYZ bullet with action verb, metric, and context",
      "action_verb": "Lead Action Verb (e.g., Architected)",
      "key_skill": "Matched Job Competency (e.g., Distributed Systems)",
      "impact_metric": "Framed outcome metric (e.g., 35% throughput increase)"
    }
  ]
}
"""


def extract_raw_bullets(raw_text: str) -> List[str]:
    """Parse raw resume text into a clean list of individual bullet strings.
    
    Handles dash bullets (- ), asterisks (* ), bullet points (• ),
    numbered lists (1. , 1) ), and raw newline-separated lines.
    Strips whitespace and ignores empty or trivial lines.
    """
    if not raw_text or not raw_text.strip():
        return []

    lines = raw_text.strip().splitlines()
    bullets: List[str] = []

    # Regex to strip common bullet prefixes:
    # - / * / • / +
    # 1. / 1) / [1]
    prefix_pattern = re.compile(
        r"^\s*(?:[-*•+•\u2022\u2023\u25E6\u2043\u2219]|\d+[\.\)]|\[\d+\])\s*",
        re.UNICODE,
    )

    for line in lines:
        cleaned = prefix_pattern.sub("", line).strip()
        # Filter out empty or trivially short lines (e.g., standalone punctuation)
        if len(cleaned) > 3:
            bullets.append(cleaned)

    # If no separate lines were extracted (e.g., single block of text), fall back to sentence split
    if not bullets and len(raw_text.strip()) > 3:
        sentences = re.split(r"(?<=[.!?])\s+", raw_text.strip())
        bullets = [s.strip() for s in sentences if len(s.strip()) > 3]

    return bullets


def build_prompt(job_description: str, bullets: List[str]) -> str:
    """Construct the user prompt combining job description and extracted bullets."""
    formatted_bullets = "\n".join(f"{i+1}. {b}" for i, b in enumerate(bullets))
    
    return f"""Target Job Description:
\"\"\"
{job_description.strip()}
\"\"\"

Candidate Original Bullets:
\"\"\"
{formatted_bullets}
\"\"\"

Please elevate each of the candidate bullets above to align with the target job description using the Google XYZ formula. Return valid JSON only."""
