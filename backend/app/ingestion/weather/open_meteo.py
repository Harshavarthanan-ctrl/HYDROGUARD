from datetime import datetime

import httpx

from .base import WeatherProvider
from .schemas import WeatherObservation


class OpenMeteoProvider(WeatherProvider):
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    HOURLY_VARIABLES = (
        "temperature_2m,"
        "relative_humidity_2m,"
        "precipitation,"
        "runoff,"
        "surface_pressure,"
        "wind_speed_10m"
    )

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> list[WeatherObservation]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": self.HOURLY_VARIABLES,
            "forecast_days": 2,
            "timezone": "Asia/Kolkata",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.BASE_URL, params=params)

            if response.status_code != 200:
                raise RuntimeError(
                    f"Open-Meteo API error "
                    f"{response.status_code}: {response.text}"
                )

            data = response.json()

        hourly = data["hourly"]

        observations = []

        for index, timestamp in enumerate(hourly["time"]):
            observations.append(
                WeatherObservation(
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=datetime.fromisoformat(timestamp),
                    temperature_c=hourly["temperature_2m"][index],
                    relative_humidity_pct=hourly["relative_humidity_2m"][index],
                    precipitation_mm=hourly["precipitation"][index],
                    surface_runoff_mm=hourly["runoff"][index],
                    surface_pressure_hpa=hourly["surface_pressure"][index],
                    wind_speed_kmh=hourly["wind_speed_10m"][index],
                    source="open-meteo",
                )
            )

        return observations