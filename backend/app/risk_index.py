"""
HydroGuard ward-level risk index.

Combines weather hazard and drainage vulnerability into a
0-100 heuristic risk index.

This is an index, NOT a calibrated probability of flooding.
"""

WEATHER_WEIGHT = 0.60
DRAINAGE_WEIGHT = 0.40


def calculate_risk_index(
    weather_hazard: float | None,
    drainage_vulnerability: float | None,
) -> float | None:
    """
    Calculate the HydroGuard Risk Index.

    Weather contributes 60%.
    Drainage vulnerability contributes 40%.

    If either component is unavailable, the combined index is
    not calculated.
    """
    if weather_hazard is None or drainage_vulnerability is None:
        return None

    if not 0 <= weather_hazard <= 100:
        raise ValueError("weather_hazard must be between 0 and 100")

    if not 0 <= drainage_vulnerability <= 100:
        raise ValueError(
            "drainage_vulnerability must be between 0 and 100"
        )

    score = (
        WEATHER_WEIGHT * weather_hazard
        + DRAINAGE_WEIGHT * drainage_vulnerability
    )

    return round(score, 2)