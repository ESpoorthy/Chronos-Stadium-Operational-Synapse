"""
Multi-agent LangGraph pipeline — the Chronos Future Engine.
Uses structured logging instead of print() for production observability.
"""
import logging
from typing import TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)


# ─── Agent State ──────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    scenario: str
    stadium_data: dict
    simulated_futures: List[dict]


# ─── Agent Nodes ──────────────────────────────────────────────────────────────

def planner_agent(state: AgentState) -> dict:
    """
    Planner agent: analyzes the incoming scenario and prepares context
    for downstream specialist agents.
    """
    logger.info("Planner Agent analyzing scenario: %s", state["scenario"])
    return {"messages": [AIMessage(content="Planner analyzed the scenario.")]}


def crowd_agent(state: AgentState) -> dict:
    """
    Crowd agent: evaluates crowd density data and identifies congestion risks.
    """
    crowd_density = state.get("stadium_data", {}).get("crowd_density", 0)
    logger.info("Crowd Agent processing — current density: %d%%", crowd_density)
    return {"messages": [AIMessage(content="Crowd agent evaluated congestion risks.")]}


def weather_agent(state: AgentState) -> dict:
    """
    Weather agent: evaluates weather telemetry and its operational impact.
    """
    weather = state.get("stadium_data", {}).get("weather_condition", "unknown")
    logger.info("Weather Agent processing — condition: %s", weather)
    return {"messages": [AIMessage(content="Weather agent evaluated impact of rain.")]}


def future_generator_agent(state: AgentState) -> dict:
    """
    Future generator agent: synthesizes agent reports into ranked simulated futures
    with probability scores and operational recommendations.
    """
    logger.info("Future Generator synthesizing simulated futures for scenario: %s", state["scenario"])

    mock_futures = [
        {
            "probability": 85,
            "risk_score": 7.5,
            "description": "High congestion at Gate C due to weather and crowd arrival.",
            "operational_impact": "Severe",
            "recommended_decision": "Open Gate D immediately.",
        },
        {
            "probability": 40,
            "risk_score": 4.0,
            "description": "Moderate congestion, crowd naturally disperses.",
            "operational_impact": "Low",
            "recommended_decision": "Monitor situation.",
        },
    ]

    logger.info("Generated %d simulated futures.", len(mock_futures))
    return {
        "simulated_futures": mock_futures,
        "messages": [AIMessage(content="Simulated futures generated.")],
    }


# ─── Graph Builder ────────────────────────────────────────────────────────────

def build_future_engine():
    """
    Constructs and compiles the LangGraph multi-agent workflow.
    Linear flow: planner → crowd → weather → generator → END
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_agent)
    workflow.add_node("crowd", crowd_agent)
    workflow.add_node("weather", weather_agent)
    workflow.add_node("generator", future_generator_agent)

    workflow.add_edge("planner", "crowd")
    workflow.add_edge("crowd", "weather")
    workflow.add_edge("weather", "generator")
    workflow.add_edge("generator", END)

    workflow.set_entry_point("planner")

    return workflow.compile()


engine = build_future_engine()
