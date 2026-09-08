"""
HydroGuard risk API endpoints.
"""

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
    weather_hazard: float | None
    drainage_vulnerability: float | None
    hydroguard_risk_index: float | None
    risk_category: str | None
    weather_data_available: bool
    drainage_data_available: bool


def row_to_ward_risk(row) -> WardRiskResponse:
    """Convert a database row into the public API response model."""

    return WardRiskResponse(
        ward=row[0],
        zone=row[1],
        weather_hazard=row[2],
        drainage_vulnerability=row[3],
        hydroguard_risk_index=row[4],
        risk_category=row[5],
        weather_data_available=row[6],
        drainage_data_available=row[7],
    )


@router.get("/wards")
def get_ward_risks():
    """Return HydroGuard risk scores for all wards."""

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ward,
                    zone,
                    weather_hazard,
                    drainage_vulnerability,
                    hydroguard_risk_index,
                    risk_category,
                    weather_data_available,
                    drainage_data_available
                FROM risk.ward_risk_scores
                ORDER BY ward;
                """
            )

            rows = cursor.fetchall()

    return {
        "count": len(rows),
        "wards": [row_to_ward_risk(row) for row in rows],
    }


@router.get("/wards/{ward}", response_model=WardRiskResponse)
def get_ward_risk(ward: str):
    """Return HydroGuard risk information for one ward."""

    ward = ward.strip().zfill(3)

    if not ward.isdigit() or len(ward) != 3:
        raise HTTPException(
            status_code=400,
            detail="Ward must be a valid numeric ward ID.",
        )

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ward,
                    zone,
                    weather_hazard,
                    drainage_vulnerability,
                    hydroguard_risk_index,
                    risk_category,
                    weather_data_available,
                    drainage_data_available
                FROM risk.ward_risk_scores
                WHERE ward = %s;
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