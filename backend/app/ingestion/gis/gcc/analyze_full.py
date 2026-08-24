from .client import fetch_all_drainage
from .processor import process_drainage_geojson


def main():
    print("Downloading complete GCC drainage network...")

    geojson = fetch_all_drainage()

    print(
        f"Downloaded features: "
        f"{len(geojson['features'])}"
    )

    print("\nProcessing spatial dataset...")

    gdf = process_drainage_geojson(geojson)

    print("\n=== HYDROGUARD GCC DRAINAGE QUALITY REPORT ===")

    print(f"Features: {len(gdf):,}")
    print(f"CRS: {gdf.crs}")

    projected = gdf.to_crs("EPSG:32644")

    total_geometry_km = (
        projected.geometry.length.sum() / 1000
    )

    print(
        f"Geometry length: "
        f"{total_geometry_km:,.3f} km"
    )

    print(
        f"Reported drainage length: "
        f"{gdf['dlen_km'].sum():,.3f} km"
    )

    print(
        f"Zones: "
        f"{gdf['zone'].nunique()}"
    )

    print(
        f"Wards: "
        f"{gdf['ward'].nunique()}"
    )

    print(
        f"Invalid geometries: "
        f"{(~gdf.geometry.is_valid).sum()}"
    )

    print(
        f"Missing geometries: "
        f"{gdf.geometry.isna().sum()}"
    )

    print(
        f"Missing width: "
        f"{gdf['drain_width_m'].isna().sum()}"
    )

    print(
        f"Missing depth: "
        f"{gdf['drain_depth_m'].isna().sum()}"
    )

    print("\nDrain types:")
    print(gdf["drain_type"].value_counts(dropna=False))

    print("\nStatus:")
    print(gdf["status"].value_counts(dropna=False))

    print("\nWater flow:")
    print(gdf["water_flow"].value_counts(dropna=False))

    print("\nOpen / Closed:")
    print(gdf["drain_detl"].value_counts(dropna=False))

    print("\nZones:")
    print(gdf["zone"].value_counts().sort_index())


if __name__ == "__main__":
    main()