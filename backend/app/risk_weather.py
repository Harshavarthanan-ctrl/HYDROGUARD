"""
Weather hazard scoring for HydroGuard.

This module converts forecast precipitation into a bounded 0-100
weather hazard score.

The thresholds are configurable and are intentionally treated as
heuristic design parameters, not calibrated flood probabilities.
"""


# 48-hour accumulated precipitation thresholds (mm)
TOTAL_RAIN_LOW_MM = 25.0
TOTAL_RAIN_MODERATE_MM = 50.0
TOTAL_RAIN_HIGH_MM = 100.0

# Maximum hourly precipitation thresholds (mm)
HOURLY_RAIN_LOW_MM = 10.0
HOURLY_RAIN_MODERATE_MM = 25.0
HOURLY_RAIN_HIGH_MM = 50.0


def _severity(
    value: float | None,
    low: float,
    moderate: float,
    high: float,
) -> float:
    """
    Convert a precipitation value into a 0-1 severity score.

    0 at/below low threshold.
    0.5 at moderate threshold.
    1.0 at/above high threshold.
    Linear interpolation is used between thresholds.
    """
    if value is None:
        return 0.0

    if value <= low:
        return 0.0

    if value <= moderate:
        return 0.5 * (value - low) / (moderate - low)

    if value <= high:
        return 0.5 + 0.5 * (value - moderate) / (high - moderate)

    return 1.0


def calculate_weather_hazard(
    total_precipitation_mm: float | None,
    max_hourly_precipitation_mm: float | None,
) -> float:
    """
    Calculate a 0-100 weather hazard score.

    Weighting:
        60% = 48-hour accumulated precipitation
        40% = maximum hourly precipitation

    This is a heuristic hazard index, NOT a probability of flooding.
    """
    total_severity = _severity(
        total_precipitation_mm,
        TOTAL_RAIN_LOW_MM,
        TOTAL_RAIN_MODERATE_MM,
        TOTAL_RAIN_HIGH_MM,
    )

    hourly_severity = _severity(
        max_hourly_precipitation_mm,
        HOURLY_RAIN_LOW_MM,
        HOURLY_RAIN_MODERATE_MM,
        HOURLY_RAIN_HIGH_MM,
    )

    score = (
        0.60 * total_severity
        + 0.40 * hourly_severity
    )

    return round(score * 100.0, 2)