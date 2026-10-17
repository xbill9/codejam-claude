"""Unit tests for Resume Tailor parsing, prompt construction, and schema validation."""

import pytest
from pydantic import ValidationError

from backend.models import TailorRequest, TailorResponse, TailoredBullet
from backend.prompts import extract_raw_bullets, build_prompt


class TestBulletExtraction:
    """Unit tests for extract_raw_bullets function."""

    def test_extract_dash_bullets(self):
        text = "- Built microservices in Python\n- Migrated database to PostgreSQL\n- Wrote unit tests"
        bullets = extract_raw_bullets(text)
        assert len(bullets) == 3
        assert bullets[0] == "Built microservices in Python"
        assert bullets[1] == "Migrated database to PostgreSQL"
        assert bullets[2] == "Wrote unit tests"

    def test_extract_asterisk_and_unicode_bullets(self):
        text = "* Spearheaded API gateway\n• Monitored Kubernetes clusters\n+ Automated deployment scripts"
        bullets = extract_raw_bullets(text)
        assert len(bullets) == 3
        assert bullets[0] == "Spearheaded API gateway"
        assert bullets[1] == "Monitored Kubernetes clusters"
        assert bullets[2] == "Automated deployment scripts"

    def test_extract_numbered_lists(self):
        text = "1. Designed distributed caching with Redis\n2) Reduced AWS infrastructure spend by 20%\n3. Led sprint planning"
        bullets = extract_raw_bullets(text)
        assert len(bullets) == 3
        assert bullets[0] == "Designed distributed caching with Redis"
        assert bullets[1] == "Reduced AWS infrastructure spend by 20%"
        assert bullets[2] == "Led sprint planning"

    def test_extract_strips_empty_lines_and_whitespace(self):
        text = "\n\n  - Cleaned data pipelines   \n\n\n  * Refactored auth middleware  \n  \n"
        bullets = extract_raw_bullets(text)
        assert len(bullets) == 2
        assert bullets[0] == "Cleaned data pipelines"
        assert bullets[1] == "Refactored auth middleware"

    def test_extract_strips_trivial_fluff(self):
        text = "-\n*\n- Real bullet here\n.\n"
        bullets = extract_raw_bullets(text)
        assert len(bullets) == 1
        assert bullets[0] == "Real bullet here"


class TestRequestValidation:
    """Unit tests for TailorRequest Pydantic model validation."""

    def test_valid_request(self):
        req = TailorRequest(
            job_description="Seeking a Senior Python Engineer with 5+ years of experience in distributed systems.",
            resume_text="• Built high throughput backend systems in Python and FastAPI",
        )
        assert req.job_description.startswith("Seeking a Senior")
        assert req.resume_text.startswith("• Built high")

    def test_empty_and_whitespace_only_job_description_raises(self):
        with pytest.raises(ValidationError):
            TailorRequest(
                job_description="   \n\t   ",
                resume_text="• Valid resume bullet that is sufficiently long",
            )

    def test_empty_and_whitespace_only_resume_raises(self):
        with pytest.raises(ValidationError):
            TailorRequest(
                job_description="Seeking a Senior Python Engineer with 5+ years of experience in distributed systems.",
                resume_text="   \n   ",
            )

    def test_short_inputs_raise_validation_error(self):
        with pytest.raises(ValidationError):
            TailorRequest(
                job_description="Too short",
                resume_text="• Valid resume bullet that is sufficiently long",
            )

    def test_exceeding_max_characters_raises(self):
        oversized = "A" * 15001
        with pytest.raises(ValidationError):
            TailorRequest(
                job_description=oversized,
                resume_text="• Valid resume bullet that is sufficiently long",
            )


class TestPromptConstruction:
    """Unit tests for build_prompt function."""

    def test_build_prompt_contains_job_and_bullets(self):
        job = "Looking for a Staff Engineer to lead Kubernetes infrastructure."
        bullets = ["Managed EKS clusters", "Tuned networking configs"]
        prompt = build_prompt(job, bullets)

        assert "Staff Engineer to lead Kubernetes infrastructure" in prompt
        assert "1. Managed EKS clusters" in prompt
        assert "2. Tuned networking configs" in prompt
        assert "Google XYZ" in prompt


class TestResponseValidation:
    """Unit tests for TailorResponse and TailoredBullet parsing."""

    def test_valid_response_parsing(self):
        data = {
            "role_summary": "Lead Infrastructure Architect",
            "bullets": [
                {
                    "original": "Managed Kubernetes",
                    "tailored": "Architected multi-region Kubernetes platform across 40 nodes, achieving 99.99% uptime.",
                    "action_verb": "Architected",
                    "key_skill": "Kubernetes",
                    "impact_metric": "achieving 99.99% uptime",
                }
            ],
        }
        resp = TailorResponse.model_validate(data)
        assert resp.role_summary == "Lead Infrastructure Architect"
        assert len(resp.bullets) == 1
        assert resp.bullets[0].action_verb == "Architected"

    def test_response_defaults_for_missing_optional_fields(self):
        data = {
            "bullets": [
                {
                    "original": "Wrote backend code",
                    "tailored": "Engineered REST APIs handling 5M daily requests.",
                }
            ]
        }
        resp = TailorResponse.model_validate(data)
        assert resp.role_summary == "Target Role Alignment"
        assert resp.bullets[0].action_verb == "Engineered"
        assert resp.bullets[0].key_skill == "Key Competency"
        assert resp.bullets[0].impact_metric == "Quantified Impact"
