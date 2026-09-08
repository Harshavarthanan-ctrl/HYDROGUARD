import asyncio

import psycopg

from backend.app.risk_refresh import refresh_all_risk_data

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


async def fetch_citywide_weather() -> dict[str, int]:
    """
    Fetch and persist weather observations for all wards.

    After ingestion completes, refresh all ward-level risk data.

    Returns ingestion and refresh statistics.
    """

    locations = get_ward_locations()

    if len(locations) != 200:
        raise ValueError(
            f"Expected 200 ward locations, found {len(locations)}"
        )

    provider = OpenMeteoProvider()

    total_fetched = 0
    total_saved = 0
    successful_wards = 0
    failed_wards = 0

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
            successful_wards += 1

            print(
                f"    Fetched: {len(observations)}, "
                f"Saved: {saved}"
            )

        except Exception as exc:
            failed_wards += 1

            print(
                f"    ERROR: {exc}"
            )

    print("=== CITYWIDE WEATHER COMPLETE ===")
    print(f"Total observations fetched: {total_fetched}")
    print(f"Total observations saved: {total_saved}")
    print(f"Successful wards: {successful_wards}")
    print(f"Failed wards: {failed_wards}")

    if failed_wards > 0:
        print(
            "WARNING: Risk refresh will use the successfully "
            "ingested weather data."
        )

    print("=== RISK DATA REFRESH ===")

    refresh_result = refresh_all_risk_data()

    print(
        f"Wards with weather features: "
        f"{refresh_result['weather_features']}"
    )
    print(
        f"Wards with unified features: "
        f"{refresh_result['risk_features']}"
    )
    print(
        f"Wards with risk scores: "
        f"{refresh_result['risk_scores']}"
    )

    print("=== PIPELINE COMPLETE ===")

    return {
        "observations_fetched": total_fetched,
        "observations_saved": total_saved,
        "successful_wards": successful_wards,
        "failed_wards": failed_wards,
        **refresh_result,
    }


if __name__ == "__main__":
    asyncio.run(fetch_citywide_weather())