"""Data models and Pydantic schemas for Resume Tailor."""

from typing import List
from pydantic import BaseModel, Field, field_validator


class TailorRequest(BaseModel):
    job_description: str = Field(
        ...,
        max_length=15000,
        description="Target job posting text",
    )
    resume_text: str = Field(
        ...,
        max_length=15000,
        description="Raw resume text or bullet points",
    )

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 20:
            raise ValueError("Job description must contain at least 20 non-whitespace characters.")
        if len(v) > 15000:
            raise ValueError("Job description must not exceed 15,000 characters.")
        return stripped

    @field_validator("resume_text")
    @classmethod
    def validate_resume_text(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Resume text must contain at least 10 non-whitespace characters.")
        if len(v) > 15000:
            raise ValueError("Resume text must not exceed 15,000 characters.")
        return stripped


class TailoredBullet(BaseModel):
    original: str = Field(..., description="Original raw bullet point from candidate")
    tailored: str = Field(..., description="Upgraded bullet following Google XYZ format")
    action_verb: str = Field(
        default="Engineered",
        description="High-impact lead action verb used (e.g., Spearheaded, Architected)",
    )
    key_skill: str = Field(
        default="Key Competency",
        description="Primary competency or keyword aligned to the job",
    )
    impact_metric: str = Field(
        default="Quantified Impact",
        description="Quantifiable impact or outcome framing",
    )


class TailorResponse(BaseModel):
    role_summary: str = Field(
        default="Target Role Alignment",
        description="1-sentence takeaway of the primary role requirements",
    )
    bullets: List[TailoredBullet] = Field(
        default_factory=list,
        description="List of transformed bullet point pairs",
    )
