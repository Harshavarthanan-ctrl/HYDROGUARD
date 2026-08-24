import pandas as pd

from .client import fetch_drainage_geojson
from .processor import process_drainage_geojson


def main():
    print("Fetching GCC drainage network...")

    geojson = fetch_drainage_geojson(limit=2000)

    gdf = process_drainage_geojson(geojson)

    print("\n=== GCC DRAINAGE NETWORK ANALYSIS ===")

    print(f"Records loaded: {len(gdf)}")

    print(f"\nCRS: {gdf.crs}")

    print(
        f"Total geometry length: "
        f"{gdf.geometry.to_crs('EPSG:32644').length.sum():,.2f} m"
    )

    print(
        f"Total reported drainage length: "
        f"{gdf['dlen_km'].sum():,.3f} km"
    )

    print(
        f"\nZones: "
        f"{gdf['zone'].nunique()}"
    )

    print(
        f"Wards: "
        f"{gdf['ward'].nunique()}"
    )

    print("\nDrain types:")
    print(
        gdf["drain_type"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nWater flow:")
    print(
        gdf["water_flow"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nStatus:")
    print(
        gdf["status"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nOpen / Closed:")
    print(
        gdf["drain_detl"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nObstacles:")
    print(
        gdf["has_obstacle"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nMissing width:")
    print(
        gdf["drain_width_m"]
        .isna()
        .sum()
    )

    print("\nMissing depth:")
    print(
        gdf["drain_depth_m"]
        .isna()
        .sum()
    )


if __name__ == "__main__":
    main()