import pytest

from backend.app.risk_categories import classify_risk


def test_low_risk():
    assert classify_risk(0.0) == "Low"
    assert classify_risk(24.99) == "Low"


def test_moderate_risk():
    assert classify_risk(25.0) == "Moderate"
    assert classify_risk(49.99) == "Moderate"


def test_high_risk():
    assert classify_risk(50.0) == "High"
    assert classify_risk(74.99) == "High"


def test_very_high_risk():
    assert classify_risk(75.0) == "Very High"
    assert classify_risk(100.0) == "Very High"


def test_missing_risk():
    assert classify_risk(None) is None


def test_invalid_risk_above_100():
    with pytest.raises(ValueError):
        classify_risk(100.01)


def test_invalid_risk_below_zero():
    with pytest.raises(ValueError):
        classify_risk(-0.01)