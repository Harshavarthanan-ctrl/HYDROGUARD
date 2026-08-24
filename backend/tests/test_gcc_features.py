from backend.app.ingestion.gis.gcc.features import (
    calculate_cross_section_area,
    calculate_infrastructure_score,
    build_drainage_features,
)


def test_cross_section_area():

    assert (
        calculate_cross_section_area(
            0.5,
            0.4,
        )
        == 0.2
    )


def test_cross_section_area_missing_value():

    assert (
        calculate_cross_section_area(
            None,
            0.4,
        )
        is None
    )


def test_cross_section_area_invalid_value():

    assert (
        calculate_cross_section_area(
            0,
            0.4,
        )
        is None
    )


def test_infrastructure_score_high_vulnerability():

    score = calculate_infrastructure_score(
        status="Bad",
        has_obstacle=True,
        has_water_flow=False,
        is_closed=False,
        is_covered=False,
        cross_section_area_m2=0.05,
    )

    assert score == 100


def test_infrastructure_score_good_condition():

    score = calculate_infrastructure_score(
        status="Good",
        has_obstacle=False,
        has_water_flow=True,
        is_closed=True,
        is_covered=True,
        cross_section_area_m2=1.0,
    )

    assert score == 0


def test_build_drainage_features():

    record = {
        "segment_id": 1,
        "zone": "N01",
        "ward": "001",
        "drain_type": "SWD",
        "status": "Bad",
        "water_flow": "No",
        "drain_detail": "Open",
        "drain_len_m": 100.0,
        "drain_width_m": 0.2,
        "drain_depth_m": 0.2,
        "has_obstacle": True,
        "has_water_flow": False,
        "is_closed": False,
        "is_covered": False,
        "geometry": None,
    }

    result = build_drainage_features(record)

    assert result["segment_id"] == 1
    assert result["cross_section_area_m2"] == 0.04
    assert result["has_obstacle"] is True
    assert result["infrastructure_score"] == 100