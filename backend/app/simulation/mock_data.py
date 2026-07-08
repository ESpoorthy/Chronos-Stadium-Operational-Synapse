import asyncio
import random
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from app.models.entities import SensorData

async def generate_mock_sensor_data(session: AsyncSession):
    # Simulate data for various sensors
    sensor_types = ['crowd', 'weather', 'transit', 'food', 'energy']
    locations = ['Gate A', 'Gate B', 'Gate C', 'Food Court 1', 'Metro Station Alpha']

    data = SensorData(
        sensor_type=random.choice(sensor_types),
        location=random.choice(locations),
        value=random.uniform(10.0, 100.0),
        metadata_json={"simulated": True},
        timestamp=datetime.utcnow()
    )
    session.add(data)
    await session.commit()
    print(f"Generated mock data: {data.sensor_type} at {data.location} = {data.value}")

async def mock_data_loop():
    while True:
        try:
            async with AsyncSessionLocal() as session:
                await generate_mock_sensor_data(session)
        except Exception as e:
            print(f"Error in mock data generation: {e}")
        
        # Wait a few seconds before the next update
        await asyncio.sleep(5)
