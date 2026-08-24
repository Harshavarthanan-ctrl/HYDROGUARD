import geopandas as gpd
import pandas as pd


SOURCE_CRS = "EPSG:32644"
TARGET_CRS = "EPSG:4326"


NUMERIC_FIELDS = [
    "drain_len",
    "drain_wid",
    "drain_dep",
    "dlen_km",
    "st_length(shape)",
    "invert_sp",
    "invert_ep",
]


def process_drainage_geojson(
    geojson: dict,
) -> gpd.GeoDataFrame:

    gdf = gpd.GeoDataFrame.from_features(
        geojson["features"],
        crs=SOURCE_CRS,
    )

    if gdf.empty:
        raise ValueError(
            "GCC drainage dataset contains no features"
        )

    if gdf.geometry.isna().any():
        raise ValueError(
            "GCC drainage dataset contains missing geometries"
        )

    invalid_count = (~gdf.geometry.is_valid).sum()

    if invalid_count:
        raise ValueError(
            f"Found {invalid_count} invalid geometries"
        )

    for column in NUMERIC_FIELDS:
        if column in gdf.columns:
            gdf[column] = pd.to_numeric(
                gdf[column],
                errors="coerce",
            )

    gdf["drain_width_m"] = gdf["drain_wid"]
    gdf["drain_depth_m"] = gdf["drain_dep"]

    gdf["drain_cross_section_m2"] = (
        gdf["drain_width_m"]
        * gdf["drain_depth_m"]
    )

    gdf["has_water_flow"] = (
        gdf["water_flow"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("yes")
    )

    gdf["has_obstacle"] = (
        gdf["obstacles"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
    )

    gdf["is_closed"] = (
        gdf["drain_detl"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("closed")
    )

    gdf["is_covered"] = (
        gdf["cover"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("yes")
    )

    gdf["is_good_condition"] = (
        gdf["status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("good")
    )

    return gdf.to_crs(TARGET_CRS)