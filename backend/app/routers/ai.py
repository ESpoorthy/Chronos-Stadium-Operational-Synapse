"""
AI simulation router.

Exposes the POST /ai/simulate endpoint which drives the multi-agent
future simulation pipeline.  The router is intentionally thin:
  - Input validation is handled by Pydantic (ScenarioRequest).
  - Business logic is delegated to SimulationService.
  - Error categorisation ensures internal details are never leaked.
"""
import logging
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.stadium_data import StadiumData
from app.services.simulation_service import simulation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Engine"])


# ── Request / Response schemas ────────────────────────────────────────────────

class ScenarioRequest(BaseModel):
    """Validated request body for the /ai/simulate endpoint."""

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
    """A single simulated operational future returned by the engine."""

    probability: float = Field(..., description="Estimated probability (0-100) that this future occurs.")
    risk_score: float = Field(..., description="Composite risk score (0-10).")
    description: str = Field(..., description="Human-readable description of this future scenario.")
    operational_impact: str = Field(..., description="Qualitative impact label (e.g. Severe, Moderate).")
    recommended_decision: str = Field(..., description="The highest-priority recommended action.")


class SimulationResponse(BaseModel):
    """Response body returned by the /ai/simulate endpoint."""

    futures: List[FutureItem] = Field(..., description="Ranked list of simulated futures.")
    messages: List[str] = Field(..., description="Agent status messages from the pipeline.")


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post(
    "/simulate",
    response_model=SimulationResponse,
    summary="Run multi-agent future simulation",
    description=(
        "Accepts a natural language scenario and live stadium telemetry. "
        "Returns a ranked list of simulated operational futures with risk "
        "scores and recommended decisions."
    ),
)
async def run_simulation(request: ScenarioRequest) -> SimulationResponse:
    """Run the multi-agent future simulation engine.

    Args:
        request: Validated scenario and stadium telemetry.

    Returns:
        ``SimulationResponse`` containing ranked futures and agent messages.

    Raises:
        HTTPException 422: On invalid simulation parameters (e.g. empty scenario).
        HTTPException 500: On unexpected engine failures.
    """
    try:
        result = simulation_service.run(
            scenario=request.scenario,
            stadium_data=request.stadium_data.model_dump(),
        )
        return SimulationResponse(
            futures=[FutureItem(**f) for f in result["futures"]],
            messages=result["messages"],
        )
    except ValueError as exc:
        logger.warning("Simulation validation error: %s", exc)
        raise HTTPException(status_code=422, detail="Invalid simulation parameters.")
    except Exception as exc:
        logger.error("Simulation engine error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while running the simulation. Please try again.",
        )
