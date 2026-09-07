import psycopg
from shapely.geometry import shape

from .ward_client import fetch_wards

DATABASE_URL = "postgresql://hydroguard:hydroguard_dev@localhost:5432/hydroguard"


def normalize_ward_id(value) -> str:
    """Convert GCC numeric ward IDs to the project's zero-padded format."""
    return f"{int(value):03d}"


def load_wards() -> int:
    data = fetch_wards()
    features = data.get("features", [])

    if not features:
        raise ValueError("GCC Ward API returned no features")

    rows = []

    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry")

        if geometry is None:
            raise ValueError(
                f"Ward {properties.get('pro_ward_n')} has no geometry"
            )

        ward_id = properties.get("pro_ward_n")
        zone = properties.get("pro_z_no")
        objectid = properties.get("objectid")

        if ward_id is None or objectid is None:
            raise ValueError("Ward feature is missing required identifiers")

        geom = shape(geometry)

        if geom.is_empty or not geom.is_valid:
            raise ValueError(
                f"Ward {ward_id} has invalid or empty geometry"
            )

        rows.append(
            (
                objectid,
                normalize_ward_id(ward_id),
                str(int(zone)) if zone is not None else None,
                geom.wkt,
            )
        )

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO gis.wards (
                    source_objectid,
                    ward,
                    zone,
                    geometry,
                    source
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    ST_GeomFromText(%s, 4326),
                    'GCC'
                )
                ON CONFLICT (source_objectid)
                DO UPDATE SET
                    ward = EXCLUDED.ward,
                    zone = EXCLUDED.zone,
                    geometry = EXCLUDED.geometry,
                    source = EXCLUDED.source,
                    ingested_at = NOW()
                """,
                rows,
            )

    return len(rows)


if __name__ == "__main__":
    loaded = load_wards()
    print("=== GCC WARD LOAD ===")
    print(f"Wards processed: {loaded}")