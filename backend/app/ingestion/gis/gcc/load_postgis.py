from pathlib import Path

import geopandas as gpd
import psycopg


GPKG_PATH = Path(
    "data/processed/gcc/storm_water_drain.gpkg"
)

GPKG_LAYER = "storm_water_drain"

DATABASE_URL = (
    "postgresql://hydroguard:hydroguard_dev"
    "@localhost:5432/hydroguard"
)


def clean_text(value):
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def to_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_bool(value):
    if value is None:
        return None

    value = str(value).strip().lower()

    if value in {"yes", "true", "1"}:
        return True

    if value in {"no", "false", "0"}:
        return False

    return None


def normalize_drain_type(value):
    value = clean_text(value)

    if value is None:
        return None

    value = value.replace("\n", " ").strip()

    mapping = {
        "swd": "SWD",
        "side drain": "Side Drain",
        "open drain": "Open Drain",
        "pipe line": "Pipe Line",
        "closed": "Closed",
    }

    return mapping.get(
        value.lower(),
        value,
    )


def normalize_status(value):
    value = clean_text(value)

    if value is None:
        return None

    mapping = {
        "good": "Good",
        "bad": "Bad",
    }

    return mapping.get(
        value.lower(),
        value,
    )


def normalize_water_flow(value):
    value = clean_text(value)

    if value is None:
        return None

    normalized = value.lower()

    if normalized in {"yes", "true"}:
        return "Yes"

    if normalized in {"no", "false"}:
        return "No"

    # Preserve anomalous source values.
    return value


def normalize_drain_detail(value):
    value = clean_text(value)

    if value is None:
        return None

    normalized = value.lower()

    if normalized == "closed":
        return "Closed"

    if normalized in {
        "open",
        "opened",
        "partially open",
    }:
        return "Open"

    return value


def calculate_cross_section_area(
    width,
    depth,
):
    if width is None or depth is None:
        return None

    if width <= 0 or depth <= 0:
        return None

    return width * depth


def normalize_geometry(geometry):
    if geometry is None:
        raise ValueError("Missing geometry")

    if geometry.is_empty:
        raise ValueError("Empty geometry")

    if geometry.geom_type not in {
        "LineString",
        "MultiLineString",
    }:
        raise ValueError(
            "Unsupported geometry type: "
            f"{geometry.geom_type}"
        )

    return geometry


def build_record(row):

    width = to_float(
        row.get("drain_wid")
    )

    depth = to_float(
        row.get("drain_dep")
    )

    obstacles = clean_text(
        row.get("obstacles")
    )

    drain_detail = normalize_drain_detail(
        row.get("drain_detl")
    )

    return {
        "source_objectid": int(
            row["objectid"]
        ),

        "zone": clean_text(
            row.get("zone")
        ),

        "ward": clean_text(
            row.get("ward")
        ),

        "location": clean_text(
            row.get("location")
        ),

        "drain_type": normalize_drain_type(
            row.get("drain_type")
        ),

        "cover": clean_text(
            row.get("cover")
        ),

        "drain_len_m": to_float(
            row.get("drain_len")
        ),

        "drain_width_m": width,

        "drain_depth_m": depth,

        "drain_size": clean_text(
            row.get("drain_size")
        ),

        "mh_shape": clean_text(
            row.get("mh_shape")
        ),

        "mh_size": clean_text(
            row.get("mh_size")
        ),

        "material": clean_text(
            row.get("swd_mat")
        ),

        "water_flow": normalize_water_flow(
            row.get("water_flow")
        ),

        "construction_type": clean_text(
            row.get("puca_kacha")
        ),

        "status": normalize_status(
            row.get("status")
        ),

        "drain_detail": drain_detail,

        "invert_start_m": to_float(
            row.get("invert_sp")
        ),

        "invert_end_m": to_float(
            row.get("invert_ep")
        ),

        "inlet_shape": clean_text(
            row.get("inlet_shp")
        ),

        "obstacles": obstacles,

        "reported_length_km": to_float(
            row.get("dlen_km")
        ),

        "has_water_flow": normalize_bool(
            row.get("water_flow")
        ),

        "has_obstacle": (
            obstacles is not None
        ),

        "is_closed": (
            drain_detail == "Closed"
        ),

        "is_covered": normalize_bool(
            row.get("cover")
        ),

        "cross_section_area_m2":
            calculate_cross_section_area(
                width,
                depth,
            ),
    }


def main():

    if not GPKG_PATH.exists():
        raise FileNotFoundError(
            f"GeoPackage not found: "
            f"{GPKG_PATH}"
        )

    print(
        "Reading GCC GeoPackage..."
    )

    gdf = gpd.read_file(
        GPKG_PATH,
        layer=GPKG_LAYER,
    )

    print(
        f"Source features: "
        f"{len(gdf):,}"
    )

    if len(gdf) != 11_531:
        raise ValueError(
            "Unexpected source feature count: "
            f"{len(gdf):,}"
        )

    if gdf.crs is None:
        raise ValueError(
            "Source dataset has no CRS"
        )

    gdf = gdf.to_crs(
        "EPSG:4326"
    )

    records = []

    for _, row in gdf.iterrows():

        records.append(
            build_record(row)
        )

    insert_sql = """
        INSERT INTO gis.drainage_segments (
            source_objectid,
            zone,
            ward,
            location,
            drain_type,
            cover,
            drain_len_m,
            drain_width_m,
            drain_depth_m,
            drain_size,
            mh_shape,
            mh_size,
            material,
            water_flow,
            construction_type,
            status,
            drain_detail,
            invert_start_m,
            invert_end_m,
            inlet_shape,
            obstacles,
            reported_length_km,
            has_water_flow,
            has_obstacle,
            is_closed,
            is_covered,
            cross_section_area_m2,
            geometry
        )
        VALUES (
            %(source_objectid)s,
            %(zone)s,
            %(ward)s,
            %(location)s,
            %(drain_type)s,
            %(cover)s,
            %(drain_len_m)s,
            %(drain_width_m)s,
            %(drain_depth_m)s,
            %(drain_size)s,
            %(mh_shape)s,
            %(mh_size)s,
            %(material)s,
            %(water_flow)s,
            %(construction_type)s,
            %(status)s,
            %(drain_detail)s,
            %(invert_start_m)s,
            %(invert_end_m)s,
            %(inlet_shape)s,
            %(obstacles)s,
            %(reported_length_km)s,
            %(has_water_flow)s,
            %(has_obstacle)s,
            %(is_closed)s,
            %(is_covered)s,
            %(cross_section_area_m2)s,
            ST_GeomFromText(
                %(wkt)s,
                4326
            )
        )
    """

    print(
        "Connecting to PostGIS..."
    )

    with psycopg.connect(
        DATABASE_URL
    ) as connection:

        with connection.cursor() as cursor:

            print(
                "Loading drainage segments..."
            )

            for index, (
                record,
                geometry,
            ) in enumerate(
                zip(
                    records,
                    gdf.geometry,
                ),
                start=1,
            ):

                geometry = normalize_geometry(
                    geometry
                )

                params = record.copy()

                params["wkt"] = (
                    geometry.wkt
                )

                cursor.execute(
                    insert_sql,
                    params,
                )

                if index % 1000 == 0:
                    print(
                        f"Inserted "
                        f"{index:,} / "
                        f"{len(records):,}"
                    )

        connection.commit()

    print(
        "\n=== POSTGIS LOAD COMPLETE ==="
    )


if __name__ == "__main__":
    main()