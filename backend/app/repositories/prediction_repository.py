"""
Repository for FuturePrediction persistence.

Implements the Repository pattern — all database access for simulated
futures is routed through this module, keeping SQL logic out of the
business and agent layers.
"""
from __future__ import annotations

import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import FuturePrediction

logger = logging.getLogger(__name__)


class PredictionRepository:
    """Async repository for ``FuturePrediction`` database records.

    All methods accept an ``AsyncSession`` injected via FastAPI's
    dependency injection system, making them easy to unit-test with
    a mocked session.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialise the repository with a database session.

        Args:
            session: An open async SQLAlchemy session.
        """
        self._session = session

    async def create(self, prediction: FuturePrediction) -> FuturePrediction:
        """Persist a new FuturePrediction record.

        Args:
            prediction: A fully populated ``FuturePrediction`` ORM instance.

        Returns:
            The same instance after it has been flushed and its primary key
            populated by the database.
        """
        self._session.add(prediction)
        await self._session.flush()
        await self._session.refresh(prediction)
        logger.info("Persisted FuturePrediction id=%s scenario_id=%s", prediction.id, prediction.scenario_id)
        return prediction

    async def get_by_scenario(self, scenario_id: str) -> Sequence[FuturePrediction]:
        """Retrieve all predictions for a given scenario identifier.

        Args:
            scenario_id: The UUID or slug that groups predictions from the
                same simulation run.

        Returns:
            A (possibly empty) sequence of matching ``FuturePrediction`` rows.
        """
        result = await self._session.execute(
            select(FuturePrediction)
            .where(FuturePrediction.scenario_id == scenario_id)
            .order_by(FuturePrediction.probability.desc())
        )
        rows = result.scalars().all()
        logger.debug("Found %d predictions for scenario_id=%s", len(rows), scenario_id)
        return rows

    async def get_recent(self, limit: int = 10) -> Sequence[FuturePrediction]:
        """Retrieve the most recently created predictions.

        Args:
            limit: Maximum number of records to return (default 10).

        Returns:
            Up to ``limit`` ``FuturePrediction`` rows ordered by creation
            time descending.
        """
        result = await self._session.execute(
            select(FuturePrediction)
            .order_by(FuturePrediction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
