import pytest

from backend.app.risk_index import calculate_risk_index


def test_combines_weather_and_drainage():
    score = calculate_risk_index(50.0, 50.0)

    assert score == 50.0


def test_weather_has_60_percent_weight():
    score = calculate_risk_index(100.0, 0.0)

    assert score == 60.0


def test_drainage_has_40_percent_weight():
    score = calculate_risk_index(0.0, 100.0)

    assert score == 40.0


def test_maximum_score_is_100():
    score = calculate_risk_index(100.0, 100.0)

    assert score == 100.0


def test_missing_weather_returns_none():
    assert calculate_risk_index(None, 50.0) is None


def test_missing_drainage_returns_none():
    assert calculate_risk_index(50.0, None) is None


def test_invalid_weather_is_rejected():
    with pytest.raises(ValueError):
        calculate_risk_index(101.0, 50.0)


def test_invalid_drainage_is_rejected():
    with pytest.raises(ValueError):
        calculate_risk_index(50.0, -1.0)