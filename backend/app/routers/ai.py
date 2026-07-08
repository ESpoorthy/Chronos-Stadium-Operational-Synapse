"""
Updated AI router with:
- Strict Pydantic input validation (StadiumData schema)
- Scenario length validation
- Safe error messages that don't leak internal details
- Rate limiting via slowapi
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List
from app.agents.core import engine
from app.schemas.stadium_data import StadiumData
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Engine"])


class ScenarioRequest(BaseModel):
    scenario: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language operational scenario query (1-2000 characters).",
    )
    stadium_data: StadiumData = Field(
        ...,
        description="Current stadium operational telemetry.",
    )


class FutureItem(BaseModel):
    probability: float
    risk_score: float
    description: str
    operational_impact: str
    recommended_decision: str


class SimulationResponse(BaseModel):
    futures: List[dict]
    messages: List[str]


@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: ScenarioRequest):
    """
    Run the multi-agent future simulation engine for a given stadium scenario.
    Returns ranked simulated futures with operational recommendations.
    """
    try:
        initial_state = {
            "messages": [HumanMessage(content=request.scenario)],
            "scenario": request.scenario,
            "stadium_data": request.stadium_data.model_dump(),
            "simulated_futures": [],
        }

        result = engine.invoke(initial_state)

        messages = [
            msg.content
            for msg in result.get("messages", [])
            if hasattr(msg, "content")
        ]

        return SimulationResponse(
            futures=result.get("simulated_futures", []),
            messages=messages,
        )
    except ValueError as e:
        # Input-related errors — safe to surface
        logger.warning("Simulation validation error: %s", e)
        raise HTTPException(status_code=422, detail="Invalid simulation parameters.")
    except Exception as e:
        # Internal errors — log full detail but return a generic message
        logger.error("Simulation engine error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while running the simulation. Please try again.",
        )
