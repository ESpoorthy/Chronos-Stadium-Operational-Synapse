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
    future_generator_agent,
    build_future_engine,
    AgentState,
)


# ─── Individual Agent Node Tests ─────────────────────────────────────────────

def test_planner_agent_returns_messages(mock_initial_state):
    """Planner agent should return a dict with an 'messages' list."""
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


def test_crowd_agent_message_is_ai_message(mock_initial_state):
    """Crowd agent should return an AIMessage."""
    result = crowd_agent(mock_initial_state)
    assert isinstance(result["messages"][0], AIMessage)


def test_weather_agent_returns_messages(mock_initial_state):
    """Weather agent should return a dict with a 'messages' list."""
    result = weather_agent(mock_initial_state)
    assert "messages" in result
    assert isinstance(result["messages"], list)
    assert len(result["messages"]) > 0


def test_weather_agent_message_is_ai_message(mock_initial_state):
    """Weather agent should return an AIMessage."""
    result = weather_agent(mock_initial_state)
    assert isinstance(result["messages"][0], AIMessage)


def test_future_generator_returns_futures(mock_initial_state):
    """Future generator agent should return a list of simulated futures."""
    result = future_generator_agent(mock_initial_state)
    assert "simulated_futures" in result
    assert isinstance(result["simulated_futures"], list)
    assert len(result["simulated_futures"]) > 0


def test_future_generator_futures_have_required_keys(mock_initial_state):
    """Each generated future should contain probability, risk_score, description, and recommended_decision."""
    result = future_generator_agent(mock_initial_state)
    for future in result["simulated_futures"]:
        assert "probability" in future
        assert "risk_score" in future
        assert "description" in future
        assert "recommended_decision" in future


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


# ─── Full Engine Integration Test ─────────────────────────────────────────────

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
    # Initial message + 4 agent messages = at least 4 total
    assert len(result["messages"]) >= 4


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
