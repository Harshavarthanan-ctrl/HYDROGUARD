from backend.app.ingestion.gis.gcc.client import fetch_drainage_geojson
from backend.app.ingestion.gis.gcc.processor import (
    process_drainage_geojson,
)


def test_gcc_drainage_processing():
    geojson = fetch_drainage_geojson(limit=5)

    gdf = process_drainage_geojson(geojson)

    assert len(gdf) == 5
    assert gdf.crs.to_string() == "EPSG:4326"

    assert "drain_width_m" in gdf.columns
    assert "drain_depth_m" in gdf.columns
    assert "drain_cross_section_m2" in gdf.columns
    assert "has_water_flow" in gdf.columns
    assert "has_obstacle" in gdf.columns

    assert gdf.geometry.notna().all()
    assert gdf.geometry.is_valid.all()