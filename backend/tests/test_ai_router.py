"""
Unit tests for the /ai/simulate FastAPI endpoint.
Tests cover request validation, response schema, and error handling.
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Health Checks ─────────────────────────────────────────────────────────────

def test_root_endpoint():
    """Root endpoint should return a running message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Health check endpoint should return ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── /ai/simulate Success Cases ────────────────────────────────────────────────

def test_simulate_returns_200_with_valid_payload(valid_simulate_payload):
    """A valid simulation request should return 200 with futures and messages."""
    response = client.post("/ai/simulate", json=valid_simulate_payload)
    assert response.status_code == 200
    data = response.json()
    assert "futures" in data
    assert "messages" in data
    assert isinstance(data["futures"], list)
    assert isinstance(data["messages"], list)


def test_simulate_futures_have_expected_keys(valid_simulate_payload):
    """Each future in the response should contain required operational fields."""
    response = client.post("/ai/simulate", json=valid_simulate_payload)
    assert response.status_code == 200
    futures = response.json()["futures"]
    assert len(futures) > 0
    required_keys = {"probability", "risk_score", "description", "operational_impact", "recommended_decision"}
    for future in futures:
        assert required_keys.issubset(future.keys())


def test_simulate_futures_probability_is_valid_percentage(valid_simulate_payload):
    """Probability values should be between 0 and 100."""
    response = client.post("/ai/simulate", json=valid_simulate_payload)
    futures = response.json()["futures"]
    for future in futures:
        assert 0 <= future["probability"] <= 100


def test_simulate_messages_are_strings(valid_simulate_payload):
    """Messages in the response should be a list of strings."""
    response = client.post("/ai/simulate", json=valid_simulate_payload)
    messages = response.json()["messages"]
    for msg in messages:
        assert isinstance(msg, str)


def test_simulate_futures_sorted_by_probability(valid_simulate_payload):
    """Futures should be returned with highest probability first."""
    response = client.post("/ai/simulate", json=valid_simulate_payload)
    probs = [f["probability"] for f in response.json()["futures"]]
    assert probs == sorted(probs, reverse=True)


def test_simulate_risk_score_non_negative(valid_simulate_payload):
    """All risk scores should be non-negative."""
    response = client.post("/ai/simulate", json=valid_simulate_payload)
    for future in response.json()["futures"]:
        assert future["risk_score"] >= 0


# ── /ai/simulate Validation Cases ────────────────────────────────────────────

def test_simulate_rejects_empty_scenario():
    """An empty scenario string should be rejected with 422 Unprocessable Entity."""
    payload = {
        "scenario": "",
        "stadium_data": {
            "crowd_density": 50,
            "weather_condition": "clear",
            "transit_status": "normal",
            "temperature_celsius": 20.0,
            "humidity_percent": 50.0,
            "active_gates": 4,
        },
    }
    response = client.post("/ai/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_rejects_missing_scenario():
    """A request without a scenario field should return 422."""
    payload = {
        "stadium_data": {
            "crowd_density": 50,
            "weather_condition": "clear",
            "transit_status": "normal",
            "temperature_celsius": 20.0,
            "humidity_percent": 50.0,
            "active_gates": 4,
        }
    }
    response = client.post("/ai/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_rejects_missing_stadium_data():
    """A request without stadium_data should return 422."""
    payload = {"scenario": "What if rain starts?"}
    response = client.post("/ai/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_rejects_invalid_crowd_density():
    """crowd_density above 100 should fail validation."""
    payload = {
        "scenario": "Test scenario",
        "stadium_data": {
            "crowd_density": 150,  # Invalid: > 100
            "weather_condition": "clear",
            "transit_status": "normal",
            "temperature_celsius": 20.0,
            "humidity_percent": 50.0,
            "active_gates": 4,
        },
    }
    response = client.post("/ai/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_rejects_scenario_too_long():
    """A scenario exceeding the max length should return 422."""
    payload = {
        "scenario": "A" * 2001,  # Exceeds 2000 char limit
        "stadium_data": {
            "crowd_density": 50,
            "weather_condition": "clear",
            "transit_status": "normal",
            "temperature_celsius": 20.0,
            "humidity_percent": 50.0,
            "active_gates": 4,
        },
    }
    response = client.post("/ai/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_rejects_negative_active_gates():
    """Negative active_gates should fail validation."""
    payload = {
        "scenario": "Test scenario",
        "stadium_data": {
            "crowd_density": 50,
            "weather_condition": "clear",
            "transit_status": "normal",
            "temperature_celsius": 20.0,
            "humidity_percent": 50.0,
            "active_gates": -1,  # Invalid
        },
    }
    response = client.post("/ai/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_rejects_invalid_weather_condition():
    """An unlisted weather_condition should fail validation."""
    payload = {
        "scenario": "Test scenario",
        "stadium_data": {
            "crowd_density": 50,
            "weather_condition": "tornado",  # Not in the Literal enum
            "transit_status": "normal",
            "temperature_celsius": 20.0,
            "humidity_percent": 50.0,
            "active_gates": 4,
        },
    }
    response = client.post("/ai/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_rejects_invalid_transit_status():
    """An unlisted transit_status should fail validation."""
    payload = {
        "scenario": "Test scenario",
        "stadium_data": {
            "crowd_density": 50,
            "weather_condition": "clear",
            "transit_status": "on_fire",  # Not in the Literal enum
            "temperature_celsius": 20.0,
            "humidity_percent": 50.0,
            "active_gates": 4,
        },
    }
    response = client.post("/ai/simulate", json=payload)
    assert response.status_code == 422


# ── /ai/simulate Error Handling ───────────────────────────────────────────────

def test_simulate_does_not_leak_internal_errors_on_failure(valid_simulate_payload):
    """On engine failure, the error detail should not expose raw exception messages."""
    with patch("app.services.simulation_service.engine.invoke", side_effect=RuntimeError("Internal secret DB password")):
        response = client.post("/ai/simulate", json=valid_simulate_payload)
        assert response.status_code == 500
        assert "Internal secret DB password" not in response.json().get("detail", "")


def test_simulate_returns_500_on_engine_error(valid_simulate_payload):
    """Engine failures should return HTTP 500."""
    with patch("app.services.simulation_service.engine.invoke", side_effect=RuntimeError("Engine crashed")):
        response = client.post("/ai/simulate", json=valid_simulate_payload)
        assert response.status_code == 500
