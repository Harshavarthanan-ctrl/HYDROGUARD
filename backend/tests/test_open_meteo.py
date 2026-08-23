from backend.app.ingestion.weather.open_meteo import OpenMeteoProvider


def test_parse_valid_response():
    data = {
        "hourly": {
            "time": [
                "2026-08-23T00:00",
                "2026-08-23T01:00",
            ],
            "temperature_2m": [29.6, 29.2],
            "relative_humidity_2m": [77, 76],
            "precipitation": [0.0, 1.2],
            "runoff": [None, None],
            "surface_pressure": [1005.4, 1005.0],
            "wind_speed_10m": [13.1, 12.4],
        }
    }

    observations = OpenMeteoProvider._parse_response(
        data,
        13.0827,
        80.2707,
    )

    assert len(observations) == 2
    assert observations[0].temperature_c == 29.6
    assert observations[1].precipitation_mm == 1.2
    assert observations[0].source == "open-meteo"


def test_missing_hourly_data():
    data = {}

    try:
        OpenMeteoProvider._parse_response(
            data,
            13.0827,
            80.2707,
        )
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "hourly" in str(error)


def test_missing_required_field():
    data = {
        "hourly": {
            "time": ["2026-08-23T00:00"],
            "temperature_2m": [29.6],
            "relative_humidity_2m": [77],
            "precipitation": [0.0],
            "surface_pressure": [1005.4],
            # wind_speed_10m intentionally missing
        }
    }

    try:
        OpenMeteoProvider._parse_response(
            data,
            13.0827,
            80.2707,
        )
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "wind_speed_10m" in str(error)