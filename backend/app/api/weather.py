from datetime import datetime, timezone

import psycopg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.risk_zone_names import get_zone_name


router = APIRouter(
    prefix="/api/v1/weather",
    tags=["weather"],
)


DATABASE_URL = (
    "postgresql://hydroguard:hydroguard_dev"
    "@localhost:5432/hydroguard"
)


# --------------------------------------------------
# Response Models
# --------------------------------------------------

class WeatherForecastPoint(BaseModel):
    timestamp: str
    precipitation_mm: float | None
    temperature_c: float | None
    relative_humidity_pct: float | None
    surface_runoff_mm: float | None


class WardWeatherForecastResponse(BaseModel):
    ward: str
    zone: str | None
    zone_name: str | None

    forecast_start: str | None
    forecast_end: str | None

    next_24h_precipitation_mm: float
    next_48h_precipitation_mm: float
    peak_hourly_precipitation_mm: float

    forecast: list[WeatherForecastPoint]


class CitywideRainfallPoint(BaseModel):
    timestamp: str
    total_precipitation_mm: float
    average_precipitation_mm: float
    maximum_precipitation_mm: float


class CitywideWeatherForecastResponse(BaseModel):
    forecast_start: str | None
    forecast_end: str | None

    ward_count: int

    citywide_24h_precipitation_mm: float
    citywide_48h_precipitation_mm: float

    average_24h_precipitation_mm: float
    average_48h_precipitation_mm: float

    peak_hourly_precipitation_mm: float

    # Highest rainfall forecast
    peak_rainfall_ward: str | None
    peak_rainfall_zone: str | None
    peak_rainfall_zone_name: str | None
    peak_rainfall_48h_mm: float

    # Highest HydroGuard risk
    highest_risk_ward: str | None
    highest_risk_zone: str | None
    highest_risk_zone_name: str | None
    highest_risk_index: float | None
    highest_risk_category: str | None

    hourly_forecast: list[CitywideRainfallPoint]


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def normalize_ward(ward: str) -> str:
    ward = ward.strip()

    if not ward.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Ward must be numeric.",
        )

    return ward.zfill(3)


def get_latest_forecast_timestamp():
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT MAX(timestamp)
                FROM weather.observations
                """
            )

            row = cursor.fetchone()

            return row[0] if row else None


def get_highest_risk_ward():
    """
    Return the ward with the highest current
    HydroGuard risk index.
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ward,
                    zone,
                    hydroguard_risk_index,
                    risk_category
                FROM risk.ward_risk_scores
                WHERE hydroguard_risk_index IS NOT NULL
                ORDER BY hydroguard_risk_index DESC,
                         ward ASC
                LIMIT 1
                """
            )

            row = cursor.fetchone()

            if not row:
                return None

            ward = row[0]
            zone = row[1]
            risk_index = row[2]
            risk_category = row[3]

            return {
                "ward": ward,
                "zone": zone,
                "zone_name": get_zone_name(zone),
                "risk_index": risk_index,
                "risk_category": risk_category,
            }


# --------------------------------------------------
# Ward Forecast
# --------------------------------------------------

@router.get(
    "/forecast/{ward}",
    response_model=WardWeatherForecastResponse,
)
def get_ward_forecast(
    ward: str,
):
    ward = normalize_ward(ward)

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    wwl.ward,
                    wwl.zone,
                    wo.timestamp,
                    wo.precipitation_mm,
                    wo.temperature_c,
                    wo.relative_humidity_pct,
                    wo.surface_runoff_mm
                FROM gis.ward_weather_locations wwl
                JOIN weather.observations wo
                    ON wo.latitude = wwl.latitude
                   AND wo.longitude = wwl.longitude
                WHERE wwl.ward = %s
                ORDER BY wo.timestamp DESC
                LIMIT 48
                """,
                (ward,),
            )

            rows = cursor.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No weather forecast found for ward {ward}.",
        )

    rows = list(reversed(rows))

    zone = rows[0][1]
    zone_name = get_zone_name(zone)

    forecast = [
        WeatherForecastPoint(
            timestamp=row[2].isoformat(),
            precipitation_mm=row[3],
            temperature_c=row[4],
            relative_humidity_pct=row[5],
            surface_runoff_mm=row[6],
        )
        for row in rows
    ]

    precipitation = [
        row[3]
        for row in rows
        if row[3] is not None
    ]

    next_24 = precipitation[:24]
    next_48 = precipitation[:48]

    return WardWeatherForecastResponse(
        ward=ward,
        zone=zone,
        zone_name=zone_name,
        forecast_start=(
            rows[0][2].isoformat()
        ),
        forecast_end=(
            rows[-1][2].isoformat()
        ),
        next_24h_precipitation_mm=round(
            sum(next_24),
            2,
        ),
        next_48h_precipitation_mm=round(
            sum(next_48),
            2,
        ),
        peak_hourly_precipitation_mm=round(
            max(precipitation)
            if precipitation
            else 0.0,
            2,
        ),
        forecast=forecast,
    )


# --------------------------------------------------
# Citywide Forecast
# --------------------------------------------------

@router.get(
    "/forecast",
    response_model=CitywideWeatherForecastResponse,
)
def get_citywide_forecast():

    latest_timestamp = (
        get_latest_forecast_timestamp()
    )

    if latest_timestamp is None:
        raise HTTPException(
            status_code=404,
            detail="No weather observations available.",
        )

    # --------------------------------------------------
    # Get the latest 48-hour forecast window
    # --------------------------------------------------

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    wo.latitude,
                    wo.longitude,
                    wo.timestamp,
                    wo.precipitation_mm
                FROM weather.observations wo
                WHERE wo.timestamp >= (
                    %s - INTERVAL '48 hours'
                )
                AND wo.timestamp <= %s
                ORDER BY wo.timestamp ASC
                """,
                (
                    latest_timestamp,
                    latest_timestamp,
                ),
            )

            rows = cursor.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No citywide forecast data available.",
        )

    # --------------------------------------------------
    # Group weather by timestamp
    # --------------------------------------------------

    hourly = {}

    ward_48h_totals = {}

    for latitude, longitude, timestamp, precipitation in rows:

        rainfall = (
            float(precipitation)
            if precipitation is not None
            else 0.0
        )

        timestamp_key = timestamp.isoformat()

        if timestamp_key not in hourly:
            hourly[timestamp_key] = []

        hourly[timestamp_key].append(
            {
                "latitude": latitude,
                "longitude": longitude,
                "rainfall": rainfall,
            }
        )

    # --------------------------------------------------
    # Build hourly citywide statistics
    # --------------------------------------------------

    hourly_forecast = []

    for timestamp_key, values in hourly.items():

        rainfall_values = [
            item["rainfall"]
            for item in values
        ]

        total_rainfall = sum(
            rainfall_values
        )

        average_rainfall = (
            total_rainfall / len(
                rainfall_values
            )
            if rainfall_values
            else 0.0
        )

        maximum_rainfall = (
            max(rainfall_values)
            if rainfall_values
            else 0.0
        )

        hourly_forecast.append(
            CitywideRainfallPoint(
                timestamp=timestamp_key,
                total_precipitation_mm=round(
                    total_rainfall,
                    2,
                ),
                average_precipitation_mm=round(
                    average_rainfall,
                    2,
                ),
                maximum_precipitation_mm=round(
                    maximum_rainfall,
                    2,
                ),
            )
        )

    hourly_forecast.sort(
        key=lambda item: item.timestamp
    )

    # --------------------------------------------------
    # Determine ward-level rainfall totals
    # --------------------------------------------------

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    wwl.ward,
                    wwl.zone,
                    SUM(
                        COALESCE(
                            wo.precipitation_mm,
                            0
                        )
                    ) AS rainfall_48h
                FROM gis.ward_weather_locations wwl
                JOIN weather.observations wo
                    ON wo.latitude = wwl.latitude
                   AND wo.longitude = wwl.longitude
                WHERE wo.timestamp >= (
                    %s - INTERVAL '48 hours'
                )
                AND wo.timestamp <= %s
                GROUP BY
                    wwl.ward,
                    wwl.zone
                ORDER BY rainfall_48h DESC
                LIMIT 1
                """,
                (
                    latest_timestamp,
                    latest_timestamp,
                ),
            )

            peak_rainfall_row = (
                cursor.fetchone()
            )

    if peak_rainfall_row:
        peak_rainfall_ward = (
            peak_rainfall_row[0]
        )

        peak_rainfall_zone = (
            peak_rainfall_row[1]
        )

        peak_rainfall_48h = (
            float(peak_rainfall_row[2])
        )

        peak_rainfall_zone_name = (
            get_zone_name(
                peak_rainfall_zone
            )
        )

    else:
        peak_rainfall_ward = None
        peak_rainfall_zone = None
        peak_rainfall_zone_name = None
        peak_rainfall_48h = 0.0

    # --------------------------------------------------
    # Citywide rainfall statistics
    # --------------------------------------------------

    first_24 = hourly_forecast[:24]
    first_48 = hourly_forecast[:48]

    citywide_24_total = sum(
        point.total_precipitation_mm
        for point in first_24
    )

    citywide_48_total = sum(
        point.total_precipitation_mm
        for point in first_48
    )

    average_24 = (
        sum(
            point.average_precipitation_mm
            for point in first_24
        )
    )

    average_48 = (
        sum(
            point.average_precipitation_mm
            for point in first_48
        )
    )

    peak_hourly = max(
        (
            point.maximum_precipitation_mm
            for point in hourly_forecast
        ),
        default=0.0,
    )

    ward_count = len(
        {
            (
                row[0],
                row[1],
            )
            for row in rows
        }
    )

    # --------------------------------------------------
    # Highest HydroGuard Risk
    # --------------------------------------------------

    highest_risk = (
        get_highest_risk_ward()
    )

    return CitywideWeatherForecastResponse(
        forecast_start=(
            hourly_forecast[0].timestamp
            if hourly_forecast
            else None
        ),

        forecast_end=(
            hourly_forecast[-1].timestamp
            if hourly_forecast
            else None
        ),

        ward_count=ward_count,

        citywide_24h_precipitation_mm=round(
            citywide_24_total,
            2,
        ),

        citywide_48h_precipitation_mm=round(
            citywide_48_total,
            2,
        ),

        average_24h_precipitation_mm=round(
            average_24,
            2,
        ),

        average_48h_precipitation_mm=round(
            average_48,
            2,
        ),

        peak_hourly_precipitation_mm=round(
            peak_hourly,
            2,
        ),

        peak_rainfall_ward=(
            peak_rainfall_ward
        ),

        peak_rainfall_zone=(
            peak_rainfall_zone
        ),

        peak_rainfall_zone_name=(
            peak_rainfall_zone_name
        ),

        peak_rainfall_48h_mm=round(
            peak_rainfall_48h,
            2,
        ),

        highest_risk_ward=(
            highest_risk["ward"]
            if highest_risk
            else None
        ),

        highest_risk_zone=(
            highest_risk["zone"]
            if highest_risk
            else None
        ),

        highest_risk_zone_name=(
            highest_risk["zone_name"]
            if highest_risk
            else None
        ),

        highest_risk_index=(
            round(
                highest_risk["risk_index"],
                2,
            )
            if highest_risk
            else None
        ),

        highest_risk_category=(
            highest_risk["risk_category"]
            if highest_risk
            else None
        ),

        hourly_forecast=hourly_forecast,
    )