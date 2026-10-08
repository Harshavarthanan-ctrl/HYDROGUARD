"""
HydroGuard risk API endpoints.
"""

import json

import psycopg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1/risk",
    tags=["Risk"],
)

DATABASE_URL = (
    "postgresql://hydroguard:hydroguard_dev"
    "@localhost:5432/hydroguard"
)


class WardRiskResponse(BaseModel):
    ward: str
    zone: str | None

    # Risk
    weather_hazard: float | None
    drainage_vulnerability: float | None
    hydroguard_risk_index: float | None
    risk_category: str | None

    # Weather
    observation_count: int | None
    latest_weather_timestamp: str | None
    total_precipitation_mm: float | None
    max_hourly_precipitation_mm: float | None
    avg_temperature_c: float | None
    max_temperature_c: float | None
    avg_relative_humidity_pct: float | None
    max_wind_speed_kmh: float | None
    avg_surface_pressure_hpa: float | None

    # Data availability
    weather_data_available: bool
    drainage_data_available: bool

    # Official GCC geometry
    geometry: dict | None = None

    # Risk generation timestamp
    generated_at: str | None = None


def row_to_ward_risk(row) -> WardRiskResponse:
    """Convert a database row into the public API response model."""

    geometry = None

    if row[17] is not None:
        geometry = json.loads(row[17])

    generated_at = (
        row[18].isoformat()
        if row[18] is not None
        else None
    )

    return WardRiskResponse(
        ward=row[0],
        zone=row[1],

        # Risk
        weather_hazard=row[2],
        drainage_vulnerability=row[3],
        hydroguard_risk_index=row[4],
        risk_category=row[5],

        # Weather
        observation_count=row[6],
        latest_weather_timestamp=(
            row[7].isoformat()
            if row[7] is not None
            else None
        ),
        total_precipitation_mm=row[8],
        max_hourly_precipitation_mm=row[9],
        avg_temperature_c=row[10],
        max_temperature_c=row[11],
        avg_relative_humidity_pct=row[12],
        max_wind_speed_kmh=row[13],
        avg_surface_pressure_hpa=row[14],

        # Data availability
        weather_data_available=row[15],
        drainage_data_available=row[16],

        # Geometry
        geometry=geometry,

        # Generation timestamp
        generated_at=generated_at,
    )


WARD_SELECT = """
    SELECT
        r.ward,
        r.zone,

        r.weather_hazard,
        r.drainage_vulnerability,
        r.hydroguard_risk_index,
        r.risk_category,

        f.observation_count,
        f.latest_weather_timestamp,
        f.total_precipitation_mm,
        f.max_hourly_precipitation_mm,
        f.avg_temperature_c,
        f.max_temperature_c,
        f.avg_relative_humidity_pct,
        f.max_wind_speed_kmh,
        f.avg_surface_pressure_hpa,

        r.weather_data_available,
        r.drainage_data_available,

        ST_AsGeoJSON(w.geometry),

        r.generated_at

    FROM risk.ward_risk_scores r

    LEFT JOIN risk.ward_risk_features f
        ON f.ward = r.ward

    LEFT JOIN gis.wards w
        ON w.ward = r.ward
"""


@router.get("/wards")
def get_ward_risks():
    """Return HydroGuard risk and weather intelligence for all wards."""

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                WARD_SELECT
                + """
                ORDER BY r.ward;
                """
            )

            rows = cursor.fetchall()

    return {
        "count": len(rows),
        "wards": [
            row_to_ward_risk(row)
            for row in rows
        ],
    }


@router.get(
    "/wards/{ward}",
    response_model=WardRiskResponse,
)
def get_ward_risk(ward: str):
    """Return complete HydroGuard intelligence for one ward."""

    ward = ward.strip()

    if not ward.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Ward must be a valid numeric ward ID.",
        )

    ward = ward.zfill(3)

    if len(ward) != 3:
        raise HTTPException(
            status_code=400,
            detail="Ward must be a valid numeric ward ID.",
        )

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                WARD_SELECT
                + """
                WHERE r.ward = %s;
                """,
                (ward,),
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ward {ward} not found",
        )

    return row_to_ward_risk(row)