from collections.abc import Sequence

import psycopg

from .schemas import WeatherObservation


DATABASE_URL = "postgresql://hydroguard:hydroguard_dev@localhost:5432/hydroguard"


def save_observations(observations: Sequence[WeatherObservation]) -> int:
    """Persist weather observations and return the number newly inserted."""

    if not observations:
        return 0

    rows = [
        (
            observation.latitude,
            observation.longitude,
            observation.timestamp,
            observation.temperature_c,
            observation.relative_humidity_pct,
            observation.precipitation_mm,
            observation.surface_runoff_mm,
            observation.surface_pressure_hpa,
            observation.wind_speed_kmh,
            observation.source,
        )
        for observation in observations
    ]

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            inserted = 0

            for row in rows:
                cursor.execute(
                    """
                    INSERT INTO weather.observations (
                        latitude, longitude, timestamp,
                        temperature_c, relative_humidity_pct,
                        precipitation_mm, surface_runoff_mm,
                        surface_pressure_hpa, wind_speed_kmh, source
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (latitude, longitude, timestamp, source)
                    DO NOTHING
                    RETURNING id
                    """,
                    row,
                )

                if cursor.fetchone() is not None:
                    inserted += 1

    return inserted