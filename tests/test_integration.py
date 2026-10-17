"""Integration tests for Resume Tailor API endpoints using mocked Gemini responses."""

import json
from unittest.mock import MagicMock, patch
import pytest


def test_health_endpoint(client):
    """Integration test: Verify GET /api/health returns status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data


def test_tailor_flow_mocked(client, fake_gemini_response_json):
    """Integration test: Verify happy-path POST /api/tailor with mocked Gemini response."""
    # Create mock response object
    mock_response = MagicMock()
    mock_response.text = json.dumps(fake_gemini_response_json)

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    payload = {
        "job_description": "We are seeking a Senior Cloud Backend Engineer proficient in Python, FastAPI, and Kubernetes to lead high-throughput microservices architecture.",
        "resume_text": "• Built backend APIs for user authentication\n• Managed database migrations and query optimization",
    }

    with patch("backend.generator.create_client", return_value=mock_client):
        response = client.post("/api/tailor", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "role_summary" in data
    assert "bullets" in data
    assert len(data["bullets"]) == 2

    first_bullet = data["bullets"][0]
    assert first_bullet["original"] == "Built backend APIs for user authentication"
    assert "OAuth2" in first_bullet["tailored"]
    assert first_bullet["action_verb"] == "Architected"
    assert "impact_metric" in first_bullet
    assert "key_skill" in first_bullet


def test_upstream_error_handling(client):
    """Integration test: Verify POST /api/tailor handles upstream Gemini failure gracefully."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("503 Service Unavailable: Model overloaded")

    payload = {
        "job_description": "Senior Software Engineer position requiring Python and backend systems architecture.",
        "resume_text": "• Built APIs and services\n• Maintained database clusters",
    }

    with patch("backend.generator.create_client", return_value=mock_client):
        response = client.post("/api/tailor", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "503" in data["detail"] or "Failed" in data["detail"]


def test_rate_limit_error_handling(client):
    """Integration test: Verify POST /api/tailor handles 429 rate limit with HTTP 429."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("ResourceExhausted: 429 Quota exceeded")

    payload = {
        "job_description": "Senior Software Engineer position requiring Python and backend systems architecture.",
        "resume_text": "• Built APIs and services\n• Maintained database clusters",
    }

    with patch("backend.generator.create_client", return_value=mock_client):
        response = client.post("/api/tailor", json=payload)

    assert response.status_code == 429
    data = response.json()
    assert "rate limit" in data["detail"].lower()
