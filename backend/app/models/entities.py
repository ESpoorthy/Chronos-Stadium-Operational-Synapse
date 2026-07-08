from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="operator")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    sensor_type = Column(String, index=True) # e.g., 'crowd', 'weather', 'transit', 'food'
    location = Column(String, index=True)
    value = Column(Float)
    metadata_json = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    severity = Column(String) # low, medium, high, critical
    status = Column(String, default="active") # active, resolved
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

class FuturePrediction(Base):
    __tablename__ = "future_predictions"
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(String, index=True)
    probability = Column(Float)
    risk_score = Column(Float)
    description = Column(String)
    timeline_events = Column(JSON) # list of future events
    operational_impact = Column(String)
    recommended_decision = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
