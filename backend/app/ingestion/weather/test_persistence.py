import asyncio

from .open_meteo import OpenMeteoProvider
from .repository import save_observations


async def main():
    provider = OpenMeteoProvider()

    observations = await provider.get_weather(
        latitude=13.0827,
        longitude=80.2707,
    )

    saved = save_observations(observations)

    print(f"Fetched: {len(observations)}")
    print(f"Saved: {saved}")


if __name__ == "__main__":
    asyncio.run(main())