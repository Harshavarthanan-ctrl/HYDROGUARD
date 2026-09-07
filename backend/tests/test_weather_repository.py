from datetime import datetime

from backend.app.ingestion.weather.repository import save_observations
from backend.app.ingestion.weather.schemas import WeatherObservation


def test_save_observations_empty():
    assert save_observations([]) == 0


def test_weather_observation_schema():
    observation = WeatherObservation(
        latitude=13.0827,
        longitude=80.2707,
        timestamp=datetime(2026, 8, 23, 0, 0),
        temperature_c=29.6,
        relative_humidity_pct=77.0,
        precipitation_mm=0.0,
        surface_runoff_mm=None,
        surface_pressure_hpa=1005.4,
        wind_speed_kmh=13.1,
        source="open-meteo",
    )

    assert observation.latitude == 13.0827
    assert observation.precipitation_mm == 0.0