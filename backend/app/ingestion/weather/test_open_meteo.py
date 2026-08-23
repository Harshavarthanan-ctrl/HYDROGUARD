import asyncio

from .open_meteo import OpenMeteoProvider


async def main():
    provider = OpenMeteoProvider()

    observations = await provider.get_weather(
        latitude=13.0827,
        longitude=80.2707,
    )

    print(f"Received {len(observations)} observations")

    for observation in observations[:3]:
        print(observation.model_dump())


if __name__ == "__main__":
    asyncio.run(main())