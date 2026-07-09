"""
Mock sensor data generator for local development and integration testing.

Produces randomised ``SensorData`` records at a configurable interval so
that the dashboard and AI pipeline have realistic telemetry to consume
without requiring physical hardware sensors.

Usage
-----
Run the loop as a background asyncio task from the application lifespan:

    asyncio.create_task(mock_data_loop())
"""
import asyncio
import logging
import random
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.models.entities import SensorData

logger = logging.getLogger(__name__)

_SENSOR_TYPES: list[str] = ["crowd", "weather", "transit", "food", "energy"]
_LOCATIONS: list[str] = [
    "Gate A",
    "Gate B",
    "Gate C",
    "Gate D",
    "Food Court 1",
    "Metro Station Alpha",
    "VIP Entrance",
]

# Interval (seconds) between successive mock data points
_GENERATION_INTERVAL_SECONDS: float = 5.0


async def generate_mock_sensor_data(session: AsyncSession) -> SensorData:
    """Create and persist a single randomised ``SensorData`` record.

    Args:
        session: An open async SQLAlchemy session.  The caller is
                 responsible for committing or rolling back.

    Returns:
        The newly created ``SensorData`` ORM instance after flush.
    """
    data = SensorData(
        sensor_type=random.choice(_SENSOR_TYPES),
        location=random.choice(_LOCATIONS),
        value=round(random.uniform(10.0, 100.0), 2),
        metadata_json={"simulated": True, "source": "mock_data_generator"},
        timestamp=datetime.now(tz=timezone.utc),
    )
    session.add(data)
    await session.commit()
    logger.debug(
        "Mock sensor data generated: type=%s location=%s value=%.2f",
        data.sensor_type,
        data.location,
        data.value,
    )
    return data


async def mock_data_loop() -> None:
    """Continuously generate mock sensor data at a fixed interval.

    Runs indefinitely as a background asyncio task.  Errors within a
    single iteration are logged and the loop continues — a single DB
    hiccup should not terminate data generation.
    """
    logger.info("Mock data loop started (interval=%.1fs).", _GENERATION_INTERVAL_SECONDS)
    while True:
        try:
            async with AsyncSessionLocal() as session:
                await generate_mock_sensor_data(session)
        except Exception:
            logger.exception("Error during mock sensor data generation; retrying after interval.")

        await asyncio.sleep(_GENERATION_INTERVAL_SECONDS)
