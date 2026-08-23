from abc import ABC, abstractmethod

from .schemas import WeatherObservation


class WeatherProvider(ABC):

    @abstractmethod
    async def get_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> list[WeatherObservation]:
        """Retrieve and normalize weather observations."""
        raise NotImplementedError