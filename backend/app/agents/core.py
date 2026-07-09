"""
Multi-agent LangGraph pipeline — the Chronos Future Engine.

Architecture
------------
The pipeline follows a linear fan-out model:

    planner → crowd → weather → transit → future_generator → END

Each specialist agent (crowd, weather, transit) enriches the shared
``AgentState`` with domain-specific analysis.  The ``future_generator``
then synthesises those signals into a ranked list of simulated futures.

Design decisions
----------------
- Structured logging replaces all ``print()`` calls for production
  observability.
- Futures are generated dynamically from actual stadium telemetry and
  the free-text scenario — not hard-coded.
- Risk scores are computed by ``app.utils.risk_calculator`` so the
  scoring logic is independently testable.
"""
from __future__ import annotations

import logging
import operator
from typing import Annotated, Any

from langgraph.graph import END, StateGraph
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from typing import TypedDict, List

from app.utils.risk_calculator import calculate_composite_risk, estimate_probability

logger = logging.getLogger(__name__)


# ── Scenario keyword maps ─────────────────────────────────────────────────────

_WEATHER_KEYWORDS: dict[str, list[str]] = {
    "storm": ["storm", "thunder", "lightning", "hurricane"],
    "heavy_rain": ["heavy rain", "downpour", "flooding", "flood"],
    "light_rain": ["rain", "drizzle", "shower", "wet"],
    "fog": ["fog", "foggy", "mist", "misty", "visibility"],
    "cloudy": ["cloud", "overcast", "grey", "gray"],
}

_CROWD_KEYWORDS: list[str] = [
    "crowd", "congestion", "jam", "packed", "full", "capacity",
    "overcrowded", "surge", "rush", "gate", "entry",
]

_TRANSIT_KEYWORDS: list[str] = [
    "metro", "transit", "train", "bus", "transport", "delay",
    "disruption", "closed", "cancelled", "traffic",
]

_EMERGENCY_KEYWORDS: list[str] = [
    "emergency", "medical", "fire", "evacuation", "injury",
    "incident", "security", "threat", "panic",
]


def _scenario_mentions(scenario: str, keywords: list[str]) -> bool:
    """Return True if any keyword appears in the lower-cased scenario."""
    lower = scenario.lower()
    return any(kw in lower for kw in keywords)


def _detect_weather_from_scenario(scenario: str) -> str | None:
    """Detect an explicit weather condition from the scenario text."""
    lower = scenario.lower()
    for condition, kws in _WEATHER_KEYWORDS.items():
        if any(kw in lower for kw in kws):
            return condition
    return None


# ── Agent State ───────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """Shared mutable state threaded through the LangGraph pipeline.

    Attributes:
        messages: Accumulated list of messages from all agents (append-only).
        scenario: The original natural language scenario query.
        stadium_data: Validated stadium telemetry as a plain dict.
        simulated_futures: Output list of ranked future predictions.
        crowd_analysis: Analysis summary produced by the crowd agent.
        weather_analysis: Analysis summary produced by the weather agent.
        transit_analysis: Analysis summary produced by the transit agent.
    """

    messages: Annotated[List[BaseMessage], operator.add]
    scenario: str
    stadium_data: dict
    simulated_futures: List[dict]
    crowd_analysis: str
    weather_analysis: str
    transit_analysis: str


# ── Agent Nodes ───────────────────────────────────────────────────────────────

def planner_agent(state: AgentState) -> dict:
    """Planner agent: validates context and prepares the pipeline for execution.

    Logs the incoming scenario and stadium telemetry so that downstream
    specialist agents have full context without re-reading it themselves.

    Args:
        state: The current shared pipeline state.

    Returns:
        A partial state dict containing the planner's status message.
    """
    scenario = state["scenario"]
    data = state.get("stadium_data", {})
    logger.info(
        "Planner — scenario=%r crowd=%s%% weather=%s transit=%s gates=%s",
        scenario[:80],
        data.get("crowd_density", "?"),
        data.get("weather_condition", "?"),
        data.get("transit_status", "?"),
        data.get("active_gates", "?"),
    )
    summary = (
        f"Scenario accepted: '{scenario[:120]}'. "
        f"Stadium telemetry: crowd={data.get('crowd_density')}%, "
        f"weather={data.get('weather_condition')}, "
        f"transit={data.get('transit_status')}, "
        f"active gates={data.get('active_gates')}."
    )
    return {"messages": [AIMessage(content=summary)]}


def crowd_agent(state: AgentState) -> dict:
    """Crowd agent: evaluates crowd density and identifies congestion risks.

    Combines the live ``crowd_density`` metric with scenario keywords to
    produce a plain-language congestion assessment that the future
    generator uses for narrative framing.

    Args:
        state: The current shared pipeline state.

    Returns:
        A partial state dict with a ``crowd_analysis`` string and an
        agent status message.
    """
    data = state.get("stadium_data", {})
    crowd_density: int = data.get("crowd_density", 0)
    scenario: str = state.get("scenario", "")
    active_gates: int = data.get("active_gates", 0)

    scenario_mentions_crowd = _scenario_mentions(scenario, _CROWD_KEYWORDS)

    if crowd_density >= 90:
        level, action = "critical", f"Open all available gates immediately. Only {active_gates} gates active."
    elif crowd_density >= 75:
        level, action = "high", "Deploy crowd stewards to primary entry points."
    elif crowd_density >= 55:
        level, action = "elevated", "Monitor gate queues; prepare to redirect flows."
    else:
        level, action = "normal", "No immediate crowd intervention required."

    if scenario_mentions_crowd:
        action += " Scenario directly references crowd dynamics — heightened priority."

    analysis = f"Crowd density at {crowd_density}% — congestion level: {level}. Recommendation: {action}"
    logger.info("Crowd Agent — %s", analysis)

    return {
        "crowd_analysis": analysis,
        "messages": [AIMessage(content=f"Crowd Agent: {analysis}")],
    }


def weather_agent(state: AgentState) -> dict:
    """Weather agent: evaluates weather telemetry and operational impact.

    Cross-references the live ``weather_condition`` field with any weather
    keywords present in the scenario text to produce an accurate severity
    rating and recommended protective action.

    Args:
        state: The current shared pipeline state.

    Returns:
        A partial state dict with a ``weather_analysis`` string and an
        agent status message.
    """
    data = state.get("stadium_data", {})
    weather: str = data.get("weather_condition", "clear")
    temperature: float = data.get("temperature_celsius", 20.0)
    humidity: float = data.get("humidity_percent", 50.0)
    scenario: str = state.get("scenario", "")

    # Scenario may mention a weather event not yet reflected in live telemetry
    scenario_weather = _detect_weather_from_scenario(scenario)
    effective_weather = scenario_weather or weather

    _severity_map: dict[str, tuple[str, str]] = {
        "clear": ("minimal", "No weather disruption anticipated."),
        "cloudy": ("low", "Monitor for deterioration; no action required."),
        "light_rain": ("moderate", "Deploy rain shelters and signage at entry gates."),
        "heavy_rain": ("high", "Activate covered transit corridors; alert crowd stewards."),
        "storm": ("critical", "Initiate storm protocol: suspend outdoor operations, shelter attendees."),
        "fog": ("moderate", "Increase lighting and reduce pedestrian speed limits."),
    }
    severity, recommendation = _severity_map.get(effective_weather, ("unknown", "Assess conditions manually."))

    analysis = (
        f"Weather: {effective_weather} (live: {weather}), severity={severity}. "
        f"Temp={temperature}°C, Humidity={humidity}%. {recommendation}"
    )
    logger.info("Weather Agent — %s", analysis)

    return {
        "weather_analysis": analysis,
        "messages": [AIMessage(content=f"Weather Agent: {analysis}")],
    }


def transit_agent(state: AgentState) -> dict:
    """Transit agent: evaluates transit infrastructure status.

    Correlates the live ``transit_status`` with scenario text to estimate
    the gate ingress impact of any transit disruption.

    Args:
        state: The current shared pipeline state.

    Returns:
        A partial state dict with a ``transit_analysis`` string and an
        agent status message.
    """
    data = state.get("stadium_data", {})
    transit: str = data.get("transit_status", "normal")
    scenario: str = state.get("scenario", "")

    scenario_mentions_transit = _scenario_mentions(scenario, _TRANSIT_KEYWORDS)

    _impact_map: dict[str, tuple[str, str]] = {
        "normal": ("none", "Transit is flowing normally; no additional gate pressure expected."),
        "delayed": ("moderate", "Delayed transit will cause late crowd surges — pre-position stewards."),
        "disrupted": ("high", "Transit disruption will divert large volumes to road entry; open overflow gates."),
        "closed": ("critical", "Transit closure forces all attendees to road transport; activate emergency traffic plan."),
    }
    impact, recommendation = _impact_map.get(transit, ("unknown", "Verify transit status manually."))

    if scenario_mentions_transit and transit == "normal":
        recommendation += " Scenario references transit disruption — verify live feeds."

    analysis = f"Transit status: {transit}, crowd-flow impact: {impact}. {recommendation}"
    logger.info("Transit Agent — %s", analysis)

    return {
        "transit_analysis": analysis,
        "messages": [AIMessage(content=f"Transit Agent: {analysis}")],
    }


def future_generator_agent(state: AgentState) -> dict:
    """Future generator: synthesises agent analyses into ranked simulated futures.

    Uses live telemetry, agent analyses, and scenario keywords to produce
    contextually accurate futures rather than returning static templates.
    Each future is scored with a risk value calculated by the shared
    ``risk_calculator`` utility.

    Args:
        state: The current shared pipeline state (after all specialist agents).

    Returns:
        A partial state dict with ``simulated_futures`` and a summary message.
    """
    scenario: str = state.get("scenario", "")
    data: dict[str, Any] = state.get("stadium_data", {})
    crowd_density: int = data.get("crowd_density", 50)
    weather: str = data.get("weather_condition", "clear")
    transit: str = data.get("transit_status", "normal")
    active_gates: int = data.get("active_gates", 4)
    temperature: float = data.get("temperature_celsius", 20.0)

    crowd_analysis: str = state.get("crowd_analysis", "")
    weather_analysis: str = state.get("weather_analysis", "")
    transit_analysis: str = state.get("transit_analysis", "")

    scenario_lower = scenario.lower()

    # Detect scenario focus for narrative framing
    is_weather_scenario = _scenario_mentions(scenario, sum(_WEATHER_KEYWORDS.values(), []))
    is_crowd_scenario = _scenario_mentions(scenario, _CROWD_KEYWORDS)
    is_transit_scenario = _scenario_mentions(scenario, _TRANSIT_KEYWORDS)
    is_emergency_scenario = _scenario_mentions(scenario, _EMERGENCY_KEYWORDS)

    # Compute base composite risk from live telemetry
    base_risk = calculate_composite_risk(crowd_density, weather, transit)

    # --- Future 1: Worst-case escalation ---
    escalated_risk = min(10.0, base_risk * 1.45)

    if is_emergency_scenario:
        f1_desc = (
            f"Emergency incident escalates: simultaneous medical response required while "
            f"{crowd_density}% capacity crowd attempts evacuation through {active_gates} gates."
        )
        f1_impact = "Catastrophic"
        f1_action = "Activate full emergency protocol: coordinate EMS, open all gates, initiate PA announcements."
    elif is_weather_scenario or weather in ("heavy_rain", "storm"):
        effective_weather = _detect_weather_from_scenario(scenario) or weather
        f1_desc = (
            f"{effective_weather.replace('_', ' ').title()} intensifies: crowd density reaches "
            f"{min(crowd_density + 10, 100)}%, outdoor entry points become unsafe. "
            f"Transit status: {transit}."
        )
        f1_impact = "Severe" if effective_weather == "storm" else "High"
        f1_action = f"Activate weather contingency plan: route crowds to covered gates, increase {active_gates} to maximum active gates."
    elif is_transit_scenario or transit in ("disrupted", "closed"):
        f1_desc = (
            f"Transit failure compounds crowd buildup: {crowd_density}% occupancy with all road "
            f"access strained. Gate pressure exceeds capacity of {active_gates} active gates."
        )
        f1_impact = "Severe"
        f1_action = "Open emergency overflow gates, deploy shuttle buses, notify attendees via PA and app."
    elif is_crowd_scenario or crowd_density >= 75:
        f1_desc = (
            f"Crowd surge at primary entry: density reaches critical levels ({min(crowd_density + 15, 100)}%). "
            f"Bottleneck forms with only {active_gates} gates active."
        )
        f1_impact = "High"
        f1_action = f"Open additional gates immediately, deploy crowd stewards to Gate C, activate queue management."
    else:
        f1_desc = (
            f"Compounding risk: {weather.replace('_', ' ')} conditions combine with "
            f"{crowd_density}% crowd density to create operational stress across all systems."
        )
        f1_impact = "Moderate-High"
        f1_action = "Increase monitoring frequency; pre-position response teams at high-risk nodes."

    f1_probability = estimate_probability(escalated_risk, base_probability=max(30, crowd_density - 10))

    # --- Future 2: Managed/optimistic outcome ---
    managed_risk = round(base_risk * 0.6, 2)

    if is_emergency_scenario:
        f2_desc = (
            f"Early medical response contains the incident: crowd evacuation proceeds in orderly "
            f"fashion through {active_gates} open gates with minimal secondary congestion."
        )
        f2_impact = "Contained"
        f2_action = "Maintain current emergency response; open additional exits as precaution."
    elif is_weather_scenario or weather in ("heavy_rain", "storm"):
        f2_desc = (
            f"Weather stabilises at {weather.replace('_', ' ')}: crowd adapts, sheltering reduces "
            f"gate pressure. Transit remains {transit}."
        )
        f2_impact = "Low-Moderate"
        f2_action = "Continue monitoring; keep covered corridors open but no further escalation needed."
    elif is_transit_scenario:
        f2_desc = (
            f"Transit partially recovers: delayed services resume, reducing road pressure. "
            f"Crowd at {crowd_density}% distributes evenly across {active_gates} gates."
        )
        f2_impact = "Low"
        f2_action = "Monitor transit feeds; stand down overflow shuttle contingency."
    else:
        f2_desc = (
            f"Situation remains stable: crowd at {crowd_density}% disperses naturally. "
            f"Weather ({weather.replace('_', ' ')}) and transit ({transit}) hold steady."
        )
        f2_impact = "Minimal"
        f2_action = "Standard operational monitoring; no immediate intervention required."

    f2_probability = estimate_probability(managed_risk, base_probability=max(20, 70 - crowd_density // 3))
    f2_probability = min(f2_probability, 100 - f1_probability + 15)  # Ensure plausible sum

    # --- Future 3: Partial mitigation outcome ---
    partial_risk = round(base_risk * 0.9, 2)

    f3_desc = (
        f"Partial mitigation: proactive deployment of stewards reduces gate pressure but "
        f"weather ({weather.replace('_', ' ')}) continues to affect outdoor areas. "
        f"Temperature at {temperature}°C adds to attendee discomfort."
    )
    f3_impact = "Moderate"
    f3_action = "Deploy additional refreshment and shelter points; stagger exit timings post-event."
    f3_probability = max(10, 100 - f1_probability - f2_probability + 5)

    simulated_futures = [
        {
            "probability": f1_probability,
            "risk_score": escalated_risk,
            "description": f1_desc,
            "operational_impact": f1_impact,
            "recommended_decision": f1_action,
        },
        {
            "probability": f2_probability,
            "risk_score": managed_risk,
            "description": f2_desc,
            "operational_impact": f2_impact,
            "recommended_decision": f2_action,
        },
        {
            "probability": f3_probability,
            "risk_score": partial_risk,
            "description": f3_desc,
            "operational_impact": f3_impact,
            "recommended_decision": f3_action,
        },
    ]

    # Sort by probability descending so the most likely future is listed first
    simulated_futures.sort(key=lambda f: f["probability"], reverse=True)

    logger.info(
        "Future Generator — scenario=%r generated %d futures (risks: %s).",
        scenario[:60],
        len(simulated_futures),
        [f["risk_score"] for f in simulated_futures],
    )

    return {
        "simulated_futures": simulated_futures,
        "messages": [AIMessage(content=f"Generated {len(simulated_futures)} scenario-aware simulated futures.")],
    }


# ── Graph Builder ─────────────────────────────────────────────────────────────

def build_future_engine():
    """Construct and compile the LangGraph multi-agent workflow.

    Pipeline topology (linear):
        planner → crowd → weather → transit → future_generator → END

    Returns:
        A compiled LangGraph ``CompiledGraph`` ready for ``.invoke()``.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_agent)
    workflow.add_node("crowd", crowd_agent)
    workflow.add_node("weather", weather_agent)
    workflow.add_node("transit", transit_agent)
    workflow.add_node("generator", future_generator_agent)

    workflow.add_edge("planner", "crowd")
    workflow.add_edge("crowd", "weather")
    workflow.add_edge("weather", "transit")
    workflow.add_edge("transit", "generator")
    workflow.add_edge("generator", END)

    workflow.set_entry_point("planner")

    return workflow.compile()


engine = build_future_engine()
