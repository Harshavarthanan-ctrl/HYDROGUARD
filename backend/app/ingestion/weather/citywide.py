import asyncio

import psycopg

from .open_meteo import OpenMeteoProvider
from .repository import save_observations


DATABASE_URL = (
    "postgresql://hydroguard:hydroguard_dev"
    "@localhost:5432/hydroguard"
)


def get_ward_locations() -> list[tuple[str, float, float]]:
    """Return ward, latitude, longitude for all weather locations."""

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ward, latitude, longitude
                FROM gis.ward_weather_locations
                ORDER BY ward
                """
            )
            return cursor.fetchall()


async def fetch_citywide_weather() -> None:
    locations = get_ward_locations()

    if len(locations) != 200:
        raise ValueError(
            f"Expected 200 ward locations, found {len(locations)}"
        )

    provider = OpenMeteoProvider()

    total_fetched = 0
    total_saved = 0

    print("=== CITYWIDE WEATHER INGESTION ===")
    print(f"Ward locations: {len(locations)}")

    for index, (ward, latitude, longitude) in enumerate(
        locations,
        start=1,
    ):
        print(
            f"[{index}/{len(locations)}] "
            f"Ward {ward}: "
            f"{latitude:.6f}, {longitude:.6f}"
        )

        try:
            observations = await provider.get_weather(
                latitude=latitude,
                longitude=longitude,
            )

            saved = save_observations(observations)

            total_fetched += len(observations)
            total_saved += saved

            print(
                f"    Fetched: {len(observations)}, "
                f"Saved: {saved}"
            )

        except Exception as exc:
            print(
                f"    ERROR: {exc}"
            )

    print("=== CITYWIDE WEATHER COMPLETE ===")
    print(f"Total observations fetched: {total_fetched}")
    print(f"Total observations saved: {total_saved}")


if __name__ == "__main__":
    asyncio.run(fetch_citywide_weather())