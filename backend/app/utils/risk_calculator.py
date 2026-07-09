"""Risk calculation utilities for the Chronos Stadium AI engine.

Provides deterministic, rule-based risk scoring that the multi-agent
pipeline uses to rank simulated futures before returning them to the
caller.  Keeping this logic in a dedicated utility module makes it
independently testable and easy to extend with ML-based scoring later.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ── Weights ───────────────────────────────────────────────────────────────────
# Each factor contributes a fractional weight to the composite risk score (0-10).
_WEATHER_RISK: dict[str, float] = {
    "clear": 0.0,
    "cloudy": 1.0,
    "light_rain": 2.5,
    "heavy_rain": 5.0,
    "storm": 8.0,
    "fog": 3.5,
}

_TRANSIT_RISK: dict[str, float] = {
    "normal": 0.0,
    "delayed": 3.0,
    "disrupted": 6.0,
    "closed": 9.0,
}

# Crowd density thresholds for risk contribution
_CROWD_THRESHOLDS: list[tuple[int, float]] = [
    (90, 5.0),
    (75, 3.0),
    (60, 1.5),
    (0, 0.0),
]


def crowd_risk_contribution(crowd_density: int) -> float:
    """Map crowd density percentage to a risk contribution value (0-5).

    Args:
        crowd_density: Integer percentage 0-100 representing stadium occupancy.

    Returns:
        A float risk contribution between 0.0 and 5.0.
    """
    for threshold, risk in _CROWD_THRESHOLDS:
        if crowd_density >= threshold:
            return risk
    return 0.0


def calculate_composite_risk(
    crowd_density: int,
    weather_condition: str,
    transit_status: str,
) -> float:
    """Compute a composite risk score (0-10) from stadium telemetry.

    The score aggregates three independent risk dimensions — crowd pressure,
    weather severity, and transit disruption — using fixed weights.  The
    result is clamped to [0, 10] to keep it within the declared range.

    Args:
        crowd_density: Integer percentage 0-100.
        weather_condition: One of the defined weather condition literals.
        transit_status: One of the defined transit status literals.

    Returns:
        Composite risk score as a float in [0.0, 10.0].
    """
    crowd = crowd_risk_contribution(crowd_density) * 0.4
    weather = _WEATHER_RISK.get(weather_condition, 2.0) * 0.35
    transit = _TRANSIT_RISK.get(transit_status, 3.0) * 0.25

    raw_score = crowd + weather + transit
    return round(min(raw_score, 10.0), 2)


def estimate_probability(risk_score: float, base_probability: int = 50) -> int:
    """Estimate the probability of a scenario based on its risk score.

    Higher risk does not necessarily mean higher probability — a severe
    outcome is often less likely than a moderate one.  This heuristic
    models that relationship by inverting risk for primary futures and
    scaling it normally for secondary ones.

    Args:
        risk_score: Composite risk score in [0, 10].
        base_probability: The starting probability anchor (default 50).

    Returns:
        Probability integer clamped to [5, 97].
    """
    adjusted = base_probability + int(risk_score * 3)
    return max(5, min(97, adjusted))
