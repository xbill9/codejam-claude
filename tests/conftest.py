"""Pytest configuration and shared fixtures."""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def fake_gemini_response_json():
    """Realistic fake structured response from Gemini."""
    return {
        "role_summary": "Senior Cloud Backend Engineer focusing on high-throughput microservices",
        "bullets": [
            {
                "original": "Built backend APIs for user authentication",
                "tailored": "Architected and deployed OAuth2 authentication service in FastAPI across 12 microservices, reducing unauthorized login attempts by 34% while maintaining sub-40ms latency.",
                "action_verb": "Architected",
                "key_skill": "OAuth2 Security",
                "impact_metric": "reduced unauthorized attempts by 34%"
            },
            {
                "original": "Managed database migrations and query optimization",
                "tailored": "Optimized PostgreSQL indexes and partitioned high-traffic schemas, accelerating critical query response times by 45% under peak 10k req/s workloads.",
                "action_verb": "Optimized",
                "key_skill": "Database Optimization",
                "impact_metric": "accelerated query response times by 45%"
            }
        ]
    }
