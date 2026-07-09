"""
Unit tests for app.utils.risk_calculator.

Validates the deterministic risk scoring logic in isolation, ensuring
that each factor (crowd, weather, transit) contributes the expected
amount to the composite score.
"""
import pytest
from app.utils.risk_calculator import (
    calculate_composite_risk,
    crowd_risk_contribution,
    estimate_probability,
)


# ── crowd_risk_contribution ───────────────────────────────────────────────────

def test_crowd_risk_zero_at_low_density():
    """Crowd density below 60 should contribute zero risk."""
    assert crowd_risk_contribution(0) == 0.0
    assert crowd_risk_contribution(59) == 0.0


def test_crowd_risk_elevated_at_60():
    """Crowd density >= 60 should contribute 1.5 risk."""
    assert crowd_risk_contribution(60) == 1.5
    assert crowd_risk_contribution(74) == 1.5


def test_crowd_risk_high_at_75():
    """Crowd density >= 75 should contribute 3.0 risk."""
    assert crowd_risk_contribution(75) == 3.0
    assert crowd_risk_contribution(89) == 3.0


def test_crowd_risk_critical_at_90():
    """Crowd density >= 90 should contribute 5.0 risk."""
    assert crowd_risk_contribution(90) == 5.0
    assert crowd_risk_contribution(100) == 5.0


# ── calculate_composite_risk ──────────────────────────────────────────────────

def test_composite_risk_clear_normal_low_crowd():
    """Clear weather + normal transit + low crowd should yield minimal risk."""
    risk = calculate_composite_risk(30, "clear", "normal")
    assert risk == 0.0


def test_composite_risk_storm_closed_high_crowd():
    """Storm + closed transit + high crowd should yield a high composite risk."""
    risk = calculate_composite_risk(95, "storm", "closed")
    # Expected: (5.0*0.4) + (8.0*0.35) + (9.0*0.25) = 2.0 + 2.8 + 2.25 = 7.05
    assert risk == pytest.approx(7.05, abs=0.01)


def test_composite_risk_clamped_at_ten():
    """Composite risk should never exceed 10.0."""
    risk = calculate_composite_risk(100, "storm", "closed")
    assert risk <= 10.0


def test_composite_risk_non_negative():
    """Composite risk should always be >= 0.0."""
    for density in (0, 50, 100):
        for weather in ("clear", "storm"):
            for transit in ("normal", "closed"):
                assert calculate_composite_risk(density, weather, transit) >= 0.0


def test_composite_risk_unknown_weather_defaults_gracefully():
    """Unknown weather condition should not raise but return a value in range."""
    risk = calculate_composite_risk(50, "unknown_condition", "normal")
    assert 0.0 <= risk <= 10.0


# ── estimate_probability ──────────────────────────────────────────────────────

def test_estimate_probability_clamped_at_5_min():
    """Probability should never fall below 5."""
    prob = estimate_probability(0.0, base_probability=0)
    assert prob >= 5


def test_estimate_probability_clamped_at_97_max():
    """Probability should never exceed 97."""
    prob = estimate_probability(10.0, base_probability=100)
    assert prob <= 97


def test_estimate_probability_increases_with_risk():
    """Higher risk scores should yield higher probability estimates."""
    p_low = estimate_probability(1.0, base_probability=40)
    p_high = estimate_probability(8.0, base_probability=40)
    assert p_high > p_low
