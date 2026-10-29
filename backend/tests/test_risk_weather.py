from backend.app.risk_weather import calculate_weather_hazard


def test_no_rain_has_zero_hazard():
    assert calculate_weather_hazard(0.0, 0.0) == 0.0


def test_light_rain_produces_small_hazard():
    score = calculate_weather_hazard(3.4, 1.2)

    assert 0.0 < score < 10.0


def test_moderate_rain_produces_midrange_hazard():
    score = calculate_weather_hazard(50.0, 25.0)

    assert score == 65.0


def test_high_rain_produces_maximum_hazard():
    score = calculate_weather_hazard(100.0, 50.0)

    assert score == 100.0


def test_values_above_high_threshold_are_capped():
    score = calculate_weather_hazard(200.0, 100.0)

    assert score == 100.0


def test_interpolation_is_bounded():
    score = calculate_weather_hazard(15.0, 5.0)

    assert 0.0 < score < 100.0


def test_missing_weather_values_are_safe():
    assert calculate_weather_hazard(None, None) == 0.0
    assert calculate_weather_hazard(10.0, None) > 0.0
    assert calculate_weather_hazard(None, 5.0) > 0.0


def test_hazard_increases_with_rainfall():
    low = calculate_weather_hazard(3.0, 1.0)
    medium = calculate_weather_hazard(25.0, 10.0)
    high = calculate_weather_hazard(75.0, 35.0)

    assert low < medium < high