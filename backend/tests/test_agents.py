"""
Unit tests for the LangGraph multi-agent pipeline (core.py).
Tests cover individual agent node outputs and the full engine invocation.
"""
import pytest
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.core import (
    planner_agent,
    crowd_agent,
    weather_agent,
    transit_agent,
    future_generator_agent,
    build_future_engine,
    AgentState,
)


# ── Individual Agent Node Tests ───────────────────────────────────────────────

def test_planner_agent_returns_messages(mock_initial_state):
    """Planner agent should return a dict with a 'messages' list."""
    result = planner_agent(mock_initial_state)
    assert "messages" in result
    assert isinstance(result["messages"], list)
    assert len(result["messages"]) > 0


def test_planner_agent_message_is_ai_message(mock_initial_state):
    """Planner agent should return an AIMessage in the messages list."""
    result = planner_agent(mock_initial_state)
    assert isinstance(result["messages"][0], AIMessage)


def test_crowd_agent_returns_messages(mock_initial_state):
    """Crowd agent should return a dict with a 'messages' list."""
    result = crowd_agent(mock_initial_state)
    assert "messages" in result
    assert isinstance(result["messages"], list)
    assert len(result["messages"]) > 0


def test_crowd_agent_returns_analysis(mock_initial_state):
    """Crowd agent should populate crowd_analysis with a non-empty string."""
    result = crowd_agent(mock_initial_state)
    assert "crowd_analysis" in result
    assert isinstance(result["crowd_analysis"], str)
    assert len(result["crowd_analysis"]) > 0


def test_crowd_agent_message_is_ai_message(mock_initial_state):
    """Crowd agent should return an AIMessage."""
    result = crowd_agent(mock_initial_state)
    assert isinstance(result["messages"][0], AIMessage)


def test_crowd_agent_critical_density():
    """At density >= 90 crowd agent should flag critical congestion level."""
    state: AgentState = {
        "messages": [HumanMessage(content="test")],
        "scenario": "test",
        "stadium_data": {
            "crowd_density": 95,
            "weather_condition": "clear",
            "transit_status": "normal",
            "temperature_celsius": 22.0,
            "humidity_percent": 50.0,
            "active_gates": 2,
        },
        "simulated_futures": [],
        "crowd_analysis": "",
        "weather_analysis": "",
        "transit_analysis": "",
    }
    result = crowd_agent(state)
    assert "critical" in result["crowd_analysis"].lower()


def test_weather_agent_returns_messages(mock_initial_state):
    """Weather agent should return a dict with a 'messages' list."""
    result = weather_agent(mock_initial_state)
    assert "messages" in result
    assert isinstance(result["messages"], list)
    assert len(result["messages"]) > 0


def test_weather_agent_returns_analysis(mock_initial_state):
    """Weather agent should populate weather_analysis."""
    result = weather_agent(mock_initial_state)
    assert "weather_analysis" in result
    assert len(result["weather_analysis"]) > 0


def test_weather_agent_message_is_ai_message(mock_initial_state):
    """Weather agent should return an AIMessage."""
    result = weather_agent(mock_initial_state)
    assert isinstance(result["messages"][0], AIMessage)


def test_weather_agent_reflects_actual_condition(mock_initial_state):
    """Weather analysis should reference the actual weather condition from stadium_data."""
    result = weather_agent(mock_initial_state)
    # mock_initial_state has weather_condition='cloudy'
    assert "cloudy" in result["weather_analysis"].lower()


def test_weather_agent_detects_rain_in_scenario():
    """Weather agent should detect rain mentioned in the scenario text."""
    state: AgentState = {
        "messages": [HumanMessage(content="What if heavy rain starts?")],
        "scenario": "What if heavy rain starts?",
        "stadium_data": {
            "crowd_density": 50,
            "weather_condition": "clear",  # live feed still shows clear
            "transit_status": "normal",
            "temperature_celsius": 18.0,
            "humidity_percent": 60.0,
            "active_gates": 4,
        },
        "simulated_futures": [],
        "crowd_analysis": "",
        "weather_analysis": "",
        "transit_analysis": "",
    }
    result = weather_agent(state)
    # Should detect 'heavy_rain' from scenario text
    assert "heavy_rain" in result["weather_analysis"] or "high" in result["weather_analysis"].lower()


def test_transit_agent_returns_messages(mock_initial_state):
    """Transit agent should return a dict with a 'messages' list."""
    result = transit_agent(mock_initial_state)
    assert "messages" in result
    assert isinstance(result["messages"], list)
    assert len(result["messages"]) > 0


def test_transit_agent_returns_analysis(mock_initial_state):
    """Transit agent should populate transit_analysis."""
    result = transit_agent(mock_initial_state)
    assert "transit_analysis" in result
    assert len(result["transit_analysis"]) > 0


def test_transit_agent_closed_status():
    """Transit agent should flag critical impact when transit is closed."""
    state: AgentState = {
        "messages": [HumanMessage(content="Metro is closed")],
        "scenario": "Metro is closed",
        "stadium_data": {
            "crowd_density": 60,
            "weather_condition": "clear",
            "transit_status": "closed",
            "temperature_celsius": 20.0,
            "humidity_percent": 55.0,
            "active_gates": 4,
        },
        "simulated_futures": [],
        "crowd_analysis": "",
        "weather_analysis": "",
        "transit_analysis": "",
    }
    result = transit_agent(state)
    assert "critical" in result["transit_analysis"].lower()


def test_future_generator_returns_futures(mock_initial_state):
    """Future generator agent should return a list of simulated futures."""
    result = future_generator_agent(mock_initial_state)
    assert "simulated_futures" in result
    assert isinstance(result["simulated_futures"], list)
    assert len(result["simulated_futures"]) > 0


def test_future_generator_futures_have_required_keys(mock_initial_state):
    """Each generated future should contain all required operational keys."""
    result = future_generator_agent(mock_initial_state)
    required_keys = {"probability", "risk_score", "description", "operational_impact", "recommended_decision"}
    for future in result["simulated_futures"]:
        assert required_keys.issubset(future.keys()), f"Missing keys in future: {future}"


def test_future_generator_futures_probability_range(mock_initial_state):
    """All futures should have probabilities between 0 and 100."""
    result = future_generator_agent(mock_initial_state)
    for future in result["simulated_futures"]:
        assert 0 <= future["probability"] <= 100


def test_future_generator_futures_risk_score_positive(mock_initial_state):
    """All futures should have a non-negative risk_score."""
    result = future_generator_agent(mock_initial_state)
    for future in result["simulated_futures"]:
        assert future["risk_score"] >= 0


def test_future_generator_returns_messages(mock_initial_state):
    """Future generator should also return messages."""
    result = future_generator_agent(mock_initial_state)
    assert "messages" in result
    assert len(result["messages"]) > 0


def test_future_generator_sorted_by_probability(mock_initial_state):
    """Futures should be ordered with the highest probability first."""
    result = future_generator_agent(mock_initial_state)
    probs = [f["probability"] for f in result["simulated_futures"]]
    assert probs == sorted(probs, reverse=True), "Futures not sorted by probability descending"


def test_future_generator_scenario_aware_storm():
    """Generator should produce storm-specific narrative for storm scenarios."""
    state: AgentState = {
        "messages": [HumanMessage(content="What if a storm hits during the match?")],
        "scenario": "What if a storm hits during the match?",
        "stadium_data": {
            "crowd_density": 80,
            "weather_condition": "cloudy",
            "transit_status": "normal",
            "temperature_celsius": 15.0,
            "humidity_percent": 80.0,
            "active_gates": 4,
        },
        "simulated_futures": [],
        "crowd_analysis": "Crowd density at 80% — congestion level: high.",
        "weather_analysis": "Storm: critical",
        "transit_analysis": "Transit normal.",
    }
    result = future_generator_agent(state)
    descriptions = " ".join(f["description"] for f in result["simulated_futures"]).lower()
    assert "storm" in descriptions or "weather" in descriptions


# ── Full Engine Integration Tests ─────────────────────────────────────────────

def test_engine_invoke_returns_full_result(mock_initial_state):
    """Full engine invocation should return a state with messages and simulated_futures."""
    engine = build_future_engine()
    result = engine.invoke(mock_initial_state)
    assert "messages" in result
    assert "simulated_futures" in result


def test_engine_invoke_accumulates_messages(mock_initial_state):
    """After running all agents, the messages list should contain multiple entries."""
    engine = build_future_engine()
    result = engine.invoke(mock_initial_state)
    # Initial HumanMessage + 5 agent AIMessages = at least 5 total
    assert len(result["messages"]) >= 5


def test_engine_invoke_produces_futures(mock_initial_state):
    """Engine should produce at least one simulated future."""
    engine = build_future_engine()
    result = engine.invoke(mock_initial_state)
    assert len(result["simulated_futures"]) > 0


def test_engine_preserves_scenario_in_state(mock_initial_state):
    """The scenario field should be preserved through the full engine run."""
    engine = build_future_engine()
    result = engine.invoke(mock_initial_state)
    assert result["scenario"] == mock_initial_state["scenario"]


def test_engine_futures_sorted_by_probability(mock_initial_state):
    """Engine output futures should be sorted by probability descending."""
    engine = build_future_engine()
    result = engine.invoke(mock_initial_state)
    probs = [f["probability"] for f in result["simulated_futures"]]
    assert probs == sorted(probs, reverse=True)
