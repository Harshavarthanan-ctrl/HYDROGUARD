import asyncio
import logging
from datetime import datetime

import httpx

from .base import WeatherProvider
from .schemas import WeatherObservation


logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.timeout = timeout
        self.max_retries = max_retries

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

        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout
                ) as client:

                    response = await client.get(
                        self.BASE_URL,
                        params=params,
                    )

                    response.raise_for_status()
                    data = response.json()

                return self._parse_response(
                    data,
                    latitude,
                    longitude,
                )

            except (
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.HTTPStatusError,
            ) as exc:

                last_error = exc

                logger.warning(
                    "Open-Meteo request failed "
                    "(attempt %s/%s): %s",
                    attempt,
                    self.max_retries,
                    exc,
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))

        raise RuntimeError(
            "Open-Meteo request failed after "
            f"{self.max_retries} attempts"
        ) from last_error

    @staticmethod
    def _parse_response(
        data: dict,
        latitude: float,
        longitude: float,
    ) -> list[WeatherObservation]:

        if "hourly" not in data:
            raise ValueError(
                "Open-Meteo response missing 'hourly' data"
            )

        hourly = data["hourly"]

        required_fields = [
            "time",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "surface_pressure",
            "wind_speed_10m",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in hourly
        ]

        if missing_fields:
            raise ValueError(
                "Open-Meteo response missing fields: "
                + ", ".join(missing_fields)
            )

        observations = []

        for index, timestamp in enumerate(hourly["time"]):

            runoff = None

            if "runoff" in hourly:
                runoff = hourly["runoff"][index]

            observations.append(
                WeatherObservation(
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=datetime.fromisoformat(timestamp),
                    temperature_c=hourly["temperature_2m"][index],
                    relative_humidity_pct=(
                        hourly["relative_humidity_2m"][index]
                    ),
                    precipitation_mm=(
                        hourly["precipitation"][index]
                    ),
                    surface_runoff_mm=runoff,
                    surface_pressure_hpa=(
                        hourly["surface_pressure"][index]
                    ),
                    wind_speed_kmh=(
                        hourly["wind_speed_10m"][index]
                    ),
                    source="open-meteo",
                )
            )

        logger.info(
            "Parsed %s weather observations from Open-Meteo",
            len(observations),
        )

        return observations