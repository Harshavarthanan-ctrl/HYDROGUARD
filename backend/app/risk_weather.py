"""
HydroGuard weather hazard calculation.

This module converts rainfall observations into a 0-100
weather hazard index.

The thresholds are heuristic v1 design values, not
scientifically calibrated flood probabilities.
"""


def _severity(
    value: float | None,
    breakpoints: list[tuple[float, float]],
) -> float:
    """
    Convert a measurement into a 0-1 severity using
    piecewise-linear interpolation.
    """
    if value is None:
        return 0.0

    if value <= breakpoints[0][0]:
        return breakpoints[0][1]

    for (x1, y1), (x2, y2) in zip(
        breakpoints,
        breakpoints[1:],
    ):
        if value <= x2:
            if x2 == x1:
                return y2

            ratio = (value - x1) / (x2 - x1)
            return y1 + ratio * (y2 - y1)

    return breakpoints[-1][1]


# Heuristic v1 rainfall response curve.
#
# Total accumulated rainfall:
# 0 mm   -> 0%
# 5 mm   -> 10%
# 25 mm  -> 35%
# 50 mm  -> 65%
# 100 mm -> 100%
TOTAL_RAIN_BREAKPOINTS = [
    (0.0, 0.0),
    (5.0, 0.10),
    (25.0, 0.35),
    (50.0, 0.65),
    (100.0, 1.0),
]


# Maximum hourly rainfall:
# 0 mm   -> 0%
# 2 mm   -> 10%
# 10 mm  -> 35%
# 25 mm  -> 65%
# 50 mm  -> 100%
HOURLY_RAIN_BREAKPOINTS = [
    (0.0, 0.0),
    (2.0, 0.10),
    (10.0, 0.35),
    (25.0, 0.65),
    (50.0, 1.0),
]


def calculate_weather_hazard(
    total_precipitation_mm: float | None,
    max_hourly_precipitation_mm: float | None,
) -> float:
    """
    Calculate a 0-100 weather hazard index.

    The index combines:
      - 60% accumulated rainfall severity
      - 40% peak hourly rainfall severity

    This is a heuristic indicator for HydroGuard v1.
    It is NOT a flood probability or scientifically
    calibrated prediction.
    """

    total_severity = _severity(
        total_precipitation_mm,
        TOTAL_RAIN_BREAKPOINTS,
    )

    hourly_severity = _severity(
        max_hourly_precipitation_mm,
        HOURLY_RAIN_BREAKPOINTS,
    )

    hazard = (
        0.60 * total_severity
        + 0.40 * hourly_severity
    )

    return round(hazard * 100, 2)