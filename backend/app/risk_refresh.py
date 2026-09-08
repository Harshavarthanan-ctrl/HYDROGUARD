"""
HydroGuard risk data refresh pipeline.
"""

import psycopg

from backend.app.risk_categories import classify_risk
from backend.app.risk_index import calculate_risk_index
from backend.app.risk_weather import calculate_weather_hazard


DATABASE_URL = (
    "postgresql://hydroguard:hydroguard_dev"
    "@localhost:5432/hydroguard"
)


def refresh_ward_weather_features() -> int:
    """
    Rebuild ward-level weather features from stored observations.

    Returns the number of wards refreshed.
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO risk.ward_weather_features (
                    ward,
                    observation_count,
                    latest_timestamp,
                    total_precipitation_mm,
                    max_hourly_precipitation_mm,
                    avg_temperature_c,
                    max_temperature_c,
                    avg_relative_humidity_pct,
                    max_wind_speed_kmh,
                    avg_surface_pressure_hpa,
                    avg_surface_runoff_mm,
                    generated_at
                )
                SELECT
                    w.ward,
                    COUNT(o.id),
                    MAX(o.timestamp),
                    COALESCE(SUM(o.precipitation_mm), 0),
                    COALESCE(MAX(o.precipitation_mm), 0),
                    AVG(o.temperature_c),
                    MAX(o.temperature_c),
                    AVG(o.relative_humidity_pct),
                    MAX(o.wind_speed_kmh),
                    AVG(o.surface_pressure_hpa),
                    AVG(o.surface_runoff_mm),
                    NOW()
                FROM gis.ward_weather_locations w
                LEFT JOIN weather.observations o
                    ON o.latitude = w.latitude
                    AND o.longitude = w.longitude
                GROUP BY w.ward
                ORDER BY w.ward
                ON CONFLICT (ward)
                DO UPDATE SET
                    observation_count = EXCLUDED.observation_count,
                    latest_timestamp = EXCLUDED.latest_timestamp,
                    total_precipitation_mm =
                        EXCLUDED.total_precipitation_mm,
                    max_hourly_precipitation_mm =
                        EXCLUDED.max_hourly_precipitation_mm,
                    avg_temperature_c =
                        EXCLUDED.avg_temperature_c,
                    max_temperature_c =
                        EXCLUDED.max_temperature_c,
                    avg_relative_humidity_pct =
                        EXCLUDED.avg_relative_humidity_pct,
                    max_wind_speed_kmh =
                        EXCLUDED.max_wind_speed_kmh,
                    avg_surface_pressure_hpa =
                        EXCLUDED.avg_surface_pressure_hpa,
                    avg_surface_runoff_mm =
                        EXCLUDED.avg_surface_runoff_mm,
                    generated_at = NOW();
                """
            )

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM risk.ward_weather_features;
                """
            )

            count = cursor.fetchone()[0]

    return count


def refresh_ward_risk_features() -> int:
    """
    Rebuild the unified ward feature table.

    Returns the number of wards refreshed.
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO risk.ward_risk_features (
                    ward,
                    zone,
                    segment_count,
                    total_drainage_km,
                    avg_infrastructure_score,
                    max_infrastructure_score,
                    obstacle_ratio,
                    closed_ratio,
                    no_flow_ratio,
                    bad_status_ratio,
                    open_drain_ratio,
                    avg_cross_section_area_m2,
                    drainage_data_available,
                    observation_count,
                    latest_weather_timestamp,
                    total_precipitation_mm,
                    max_hourly_precipitation_mm,
                    avg_temperature_c,
                    max_temperature_c,
                    avg_relative_humidity_pct,
                    max_wind_speed_kmh,
                    avg_surface_pressure_hpa,
                    avg_surface_runoff_mm,
                    weather_data_available,
                    generated_at
                )
                SELECT
                    w.ward,
                    w.zone,

                    d.segment_count,
                    d.total_drainage_km,
                    d.avg_infrastructure_score,
                    d.max_infrastructure_score,
                    d.obstacle_ratio,
                    d.closed_ratio,
                    d.no_flow_ratio,
                    d.bad_status_ratio,
                    d.open_drain_ratio,
                    d.avg_cross_section_area_m2,

                    COALESCE(d.segment_count > 0, FALSE),

                    wf.observation_count,
                    wf.latest_timestamp,
                    wf.total_precipitation_mm,
                    wf.max_hourly_precipitation_mm,
                    wf.avg_temperature_c,
                    wf.max_temperature_c,
                    wf.avg_relative_humidity_pct,
                    wf.max_wind_speed_kmh,
                    wf.avg_surface_pressure_hpa,
                    wf.avg_surface_runoff_mm,

                    COALESCE(wf.observation_count > 0, FALSE),

                    NOW()
                FROM gis.wards w
                LEFT JOIN risk.ward_drainage_features d
                    ON d.ward = w.ward
                LEFT JOIN risk.ward_weather_features wf
                    ON wf.ward = w.ward
                ORDER BY w.ward

                ON CONFLICT (ward)
                DO UPDATE SET
                    zone = EXCLUDED.zone,
                    segment_count = EXCLUDED.segment_count,
                    total_drainage_km = EXCLUDED.total_drainage_km,
                    avg_infrastructure_score =
                        EXCLUDED.avg_infrastructure_score,
                    max_infrastructure_score =
                        EXCLUDED.max_infrastructure_score,
                    obstacle_ratio = EXCLUDED.obstacle_ratio,
                    closed_ratio = EXCLUDED.closed_ratio,
                    no_flow_ratio = EXCLUDED.no_flow_ratio,
                    bad_status_ratio = EXCLUDED.bad_status_ratio,
                    open_drain_ratio = EXCLUDED.open_drain_ratio,
                    avg_cross_section_area_m2 =
                        EXCLUDED.avg_cross_section_area_m2,
                    drainage_data_available =
                        EXCLUDED.drainage_data_available,
                    observation_count = EXCLUDED.observation_count,
                    latest_weather_timestamp =
                        EXCLUDED.latest_weather_timestamp,
                    total_precipitation_mm =
                        EXCLUDED.total_precipitation_mm,
                    max_hourly_precipitation_mm =
                        EXCLUDED.max_hourly_precipitation_mm,
                    avg_temperature_c =
                        EXCLUDED.avg_temperature_c,
                    max_temperature_c =
                        EXCLUDED.max_temperature_c,
                    avg_relative_humidity_pct =
                        EXCLUDED.avg_relative_humidity_pct,
                    max_wind_speed_kmh =
                        EXCLUDED.max_wind_speed_kmh,
                    avg_surface_pressure_hpa =
                        EXCLUDED.avg_surface_pressure_hpa,
                    avg_surface_runoff_mm =
                        EXCLUDED.avg_surface_runoff_mm,
                    weather_data_available =
                        EXCLUDED.weather_data_available,
                    generated_at = NOW();
                """
            )

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM risk.ward_risk_features;
                """
            )

            count = cursor.fetchone()[0]

    return count


def refresh_ward_risk_scores() -> int:
    """
    Recalculate the HydroGuard risk index for every ward.

    Returns the number of wards refreshed.
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ward,
                    zone,
                    total_precipitation_mm,
                    max_hourly_precipitation_mm,
                    avg_infrastructure_score,
                    weather_data_available,
                    drainage_data_available
                FROM risk.ward_risk_features
                ORDER BY ward;
                """
            )

            rows = cursor.fetchall()

            for row in rows:
                (
                    ward,
                    zone,
                    total_precipitation,
                    max_hourly_precipitation,
                    drainage_vulnerability,
                    weather_available,
                    drainage_available,
                ) = row

                weather_hazard = None

                if weather_available:
                    weather_hazard = calculate_weather_hazard(
                        total_precipitation,
                        max_hourly_precipitation,
                    )

                risk_index = None

                if weather_hazard is not None and drainage_available:
                    risk_index = calculate_risk_index(
                        weather_hazard,
                        drainage_vulnerability,
                    )

                risk_category = classify_risk(risk_index)

                cursor.execute(
                    """
                    INSERT INTO risk.ward_risk_scores (
                        ward,
                        zone,
                        weather_hazard,
                        drainage_vulnerability,
                        hydroguard_risk_index,
                        risk_category,
                        weather_data_available,
                        drainage_data_available,
                        generated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                    ON CONFLICT (ward)
                    DO UPDATE SET
                        zone = EXCLUDED.zone,
                        weather_hazard = EXCLUDED.weather_hazard,
                        drainage_vulnerability =
                            EXCLUDED.drainage_vulnerability,
                        hydroguard_risk_index =
                            EXCLUDED.hydroguard_risk_index,
                        risk_category = EXCLUDED.risk_category,
                        weather_data_available =
                            EXCLUDED.weather_data_available,
                        drainage_data_available =
                            EXCLUDED.drainage_data_available,
                        generated_at = NOW();
                    """,
                    (
                        ward,
                        zone,
                        weather_hazard,
                        drainage_vulnerability,
                        risk_index,
                        risk_category,
                        weather_available,
                        drainage_available,
                    ),
                )

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM risk.ward_risk_scores;
                """
            )

            count = cursor.fetchone()[0]

    return count


def refresh_all_risk_data() -> dict[str, int]:
    """
    Refresh all ward-level risk features and scores.
    """

    weather_count = refresh_ward_weather_features()
    feature_count = refresh_ward_risk_features()
    score_count = refresh_ward_risk_scores()

    return {
        "weather_features": weather_count,
        "risk_features": feature_count,
        "risk_scores": score_count,
    }


if __name__ == "__main__":
    result = refresh_all_risk_data()

    print("=== HYDROGUARD RISK REFRESH ===")
    print(f"Wards with weather features: {result['weather_features']}")
    print(f"Wards with unified features: {result['risk_features']}")
    print(f"Wards with risk scores: {result['risk_scores']}")
    print("=== REFRESH COMPLETE ===")