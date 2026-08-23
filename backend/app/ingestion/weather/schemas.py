from datetime import datetime

from pydantic import BaseModel, Field


class WeatherObservation(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime

    temperature_c: float | None = None
    relative_humidity_pct: float | None = Field(default=None, ge=0, le=100)
    precipitation_mm: float | None = Field(default=None, ge=0)
    surface_runoff_mm: float | None = Field(default=None, ge=0)
    surface_pressure_hpa: float | None = None
    wind_speed_kmh: float | None = Field(default=None, ge=0)

    source: str