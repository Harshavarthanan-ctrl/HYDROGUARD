from backend.app.risk_weather import calculate_weather_hazard


def test_no_rain_has_zero_hazard():
    assert calculate_weather_hazard(0.0, 0.0) == 0.0


def test_below_threshold_has_zero_hazard():
    assert calculate_weather_hazard(25.0, 10.0) == 0.0


def test_moderate_thresholds_produce_midrange_hazard():
    score = calculate_weather_hazard(50.0, 25.0)

    assert score == 50.0


def test_high_thresholds_produce_maximum_hazard():
    assert calculate_weather_hazard(100.0, 50.0) == 100.0


def test_values_above_high_threshold_are_capped():
    assert calculate_weather_hazard(200.0, 100.0) == 100.0


def test_interpolation_is_bounded():
    score = calculate_weather_hazard(75.0, 37.5)

    assert 50.0 < score < 100.0


def test_missing_weather_values_are_safe():
    assert calculate_weather_hazard(None, None) == 0.0