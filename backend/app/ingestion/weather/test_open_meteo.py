import asyncio
import logging

from .open_meteo import OpenMeteoProvider


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def main():
    provider = OpenMeteoProvider()

    observations = await provider.get_weather(
        latitude=13.0827,
        longitude=80.2707,
    )

    print(f"\nReceived {len(observations)} observations\n")

    for observation in observations[:3]:
        print(observation.model_dump())


if __name__ == "__main__":
    asyncio.run(main())