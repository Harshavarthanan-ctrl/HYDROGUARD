def calculate_cross_section_area(
    width_m: float | None,
    depth_m: float | None,
) -> float | None:
    if width_m is None or depth_m is None:
        return None

    if width_m <= 0 or depth_m <= 0:
        return None

    return round(width_m * depth_m, 6)


def calculate_infrastructure_score(
    *,
    status: str | None,
    has_obstacle: bool,
    has_water_flow: bool | None,
    is_closed: bool,
    is_covered: bool | None,
    cross_section_area_m2: float | None,
) -> float:
    """
    Engineering proxy score.

    Higher score = greater infrastructure vulnerability.
    Range: approximately 0–100.
    """

    score = 0.0

    if status and status.strip().lower() == "bad":
        score += 30

    if has_obstacle:
        score += 25

    if has_water_flow is False:
        score += 20

    if not is_closed:
        score += 10

    if is_covered is False:
        score += 5

    if (
        cross_section_area_m2 is not None
        and cross_section_area_m2 < 0.10
    ):
        score += 10

    return score


def build_drainage_features(record: dict) -> dict:
    width = record.get("drain_width_m")
    depth = record.get("drain_depth_m")

    area = calculate_cross_section_area(
        width,
        depth,
    )

    has_obstacle = bool(
        record.get("has_obstacle", False)
    )

    is_closed = bool(
        record.get("is_closed", False)
    )

    has_water_flow = record.get(
        "has_water_flow"
    )

    is_covered = record.get(
        "is_covered"
    )

    score = calculate_infrastructure_score(
        status=record.get("status"),
        has_obstacle=has_obstacle,
        has_water_flow=has_water_flow,
        is_closed=is_closed,
        is_covered=is_covered,
        cross_section_area_m2=area,
    )

    return {
        "segment_id": record["segment_id"],
        "zone": record.get("zone"),
        "ward": record.get("ward"),
        "drain_type": record.get("drain_type"),
        "status": record.get("status"),
        "water_flow": record.get("water_flow"),
        "drain_detail": record.get("drain_detail"),
        "drainage_length_m": record.get(
            "drain_len_m"
        ),
        "cross_section_area_m2": area,
        "has_obstacle": has_obstacle,
        "is_closed": is_closed,
        "is_covered": is_covered,
        "infrastructure_score": score,
        "geometry": record.get("geometry"),
    }