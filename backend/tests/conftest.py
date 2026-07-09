"""
Pytest configuration and shared fixtures for Chronos Stadium AI backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from langchain_core.messages import HumanMessage


@pytest.fixture(scope="module")
def client():
    """FastAPI test client fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_initial_state():
    """Fixture providing a valid initial agent state for testing.

    Includes all AgentState keys (including the new analysis fields
    introduced in the transit-aware pipeline refactor).
    """
    return {
        "messages": [HumanMessage(content="What if heavy rain starts at 7 PM?")],
        "scenario": "What if heavy rain starts at 7 PM?",
        "stadium_data": {
            "crowd_density": 75,
            "weather_condition": "cloudy",
            "transit_status": "normal",
            "temperature_celsius": 22.5,
            "humidity_percent": 65.0,
            "active_gates": 4,
        },
        "simulated_futures": [],
        "crowd_analysis": "",
        "weather_analysis": "",
        "transit_analysis": "",
    }


@pytest.fixture
def valid_simulate_payload():
    """Fixture providing a valid /ai/simulate request payload."""
    return {
        "scenario": "What if heavy rain starts at 7 PM?",
        "stadium_data": {
            "crowd_density": 75,
            "weather_condition": "cloudy",
            "transit_status": "normal",
            "temperature_celsius": 22.5,
            "humidity_percent": 65.0,
            "active_gates": 4,
        },
    }
