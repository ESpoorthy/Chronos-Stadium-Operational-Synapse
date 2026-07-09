"""
Simulation orchestration service.

Acts as the bridge between the FastAPI router and the LangGraph engine,
isolating the business logic from HTTP concerns and making the
simulation pipeline independently testable.
"""
from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage

from app.agents.core import engine

logger = logging.getLogger(__name__)


class SimulationService:
    """Orchestrates the multi-agent future simulation pipeline.

    Responsibilities:
    - Build the initial agent state from validated request data.
    - Invoke the LangGraph engine.
    - Extract and return clean result data.

    Keeping orchestration here (rather than in the router) means the
    router stays thin and this class is fully unit-testable without HTTP.
    """

    def run(self, scenario: str, stadium_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the future simulation engine for a given scenario.

        Args:
            scenario: A natural language operational scenario string.
            stadium_data: Validated stadium telemetry as a plain dict.

        Returns:
            A dict with keys ``futures`` (list of simulated future dicts)
            and ``messages`` (list of agent message strings).

        Raises:
            ValueError: If the scenario string is empty after stripping.
            RuntimeError: If the LangGraph engine raises an unexpected error.
        """
        stripped = scenario.strip()
        if not stripped:
            raise ValueError("Scenario must not be empty.")

        logger.info("SimulationService.run — scenario=%r crowd=%s weather=%s transit=%s",
                    stripped[:80],
                    stadium_data.get("crowd_density"),
                    stadium_data.get("weather_condition"),
                    stadium_data.get("transit_status"))

        initial_state: dict[str, Any] = {
            "messages": [HumanMessage(content=stripped)],
            "scenario": stripped,
            "stadium_data": stadium_data,
            "simulated_futures": [],
        }

        result = engine.invoke(initial_state)

        messages: list[str] = [
            msg.content
            for msg in result.get("messages", [])
            if hasattr(msg, "content")
        ]

        futures: list[dict] = result.get("simulated_futures", [])

        logger.info("Simulation complete — %d futures generated, %d messages.", len(futures), len(messages))
        return {"futures": futures, "messages": messages}


# Module-level singleton — avoids rebuilding the engine on every request.
simulation_service = SimulationService()
