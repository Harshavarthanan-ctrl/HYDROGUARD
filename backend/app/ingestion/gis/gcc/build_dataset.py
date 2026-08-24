import json
from pathlib import Path

import geopandas as gpd

from .client import fetch_all_drainage
from .processor import process_drainage_geojson


RAW_DIR = Path("data/raw/gcc")
PROCESSED_DIR = Path("data/processed/gcc")

RAW_FILE = RAW_DIR / "storm_water_drain_raw.geojson"
PROCESSED_FILE = (
    PROCESSED_DIR / "storm_water_drain.gpkg"
)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading complete GCC drainage dataset...")

    geojson = fetch_all_drainage()

    print(
        f"Downloaded {len(geojson['features']):,} features"
    )

    print("\nSaving raw GeoJSON...")

    with RAW_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            geojson,
            file,
            ensure_ascii=False,
        )

    print(f"Raw dataset: {RAW_FILE}")

    print("\nProcessing dataset...")

    gdf = process_drainage_geojson(geojson)

    print(
        f"Processed features: {len(gdf):,}"
    )

    print("\nSaving GeoPackage...")

    gdf.to_file(
        PROCESSED_FILE,
        layer="storm_water_drain",
        driver="GPKG",
    )

    print(
        f"Processed dataset: {PROCESSED_FILE}"
    )

    print("\n=== DATASET BUILD COMPLETE ===")
    print(f"Features: {len(gdf):,}")
    print(f"CRS: {gdf.crs}")
    print(
        f"Geometry valid: "
        f"{gdf.geometry.is_valid.all()}"
    )


if __name__ == "__main__":
    main()