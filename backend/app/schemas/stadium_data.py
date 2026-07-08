"""
Strict Pydantic v2 schema for stadium operational data.
Replaces the loose `dict` type in ScenarioRequest with validated, bounded fields.
"""
from pydantic import BaseModel, Field
from typing import Literal


class StadiumData(BaseModel):
    """
    Validated schema for real-time stadium operational telemetry.
    All fields are bounded and type-checked to prevent injection and data abuse.
    """

    crowd_density: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall crowd density as a percentage (0-100).",
    )
    weather_condition: Literal["clear", "cloudy", "light_rain", "heavy_rain", "storm", "fog"] = Field(
        ...,
        description="Current weather condition category.",
    )
    transit_status: Literal["normal", "delayed", "disrupted", "closed"] = Field(
        ...,
        description="Current status of transit systems serving the stadium.",
    )
    temperature_celsius: float = Field(
        ...,
        ge=-20.0,
        le=55.0,
        description="Ambient temperature in Celsius (-20 to 55).",
    )
    humidity_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Relative humidity percentage (0-100).",
    )
    active_gates: int = Field(
        ...,
        ge=0,
        le=20,
        description="Number of currently active stadium entry gates (0-20).",
    )
