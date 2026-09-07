"""
HydroGuard risk categories.

The categories are based on the theoretical 0-100
HydroGuard Risk Index.

These are heuristic bands and are not calibrated
probabilities of flooding.
"""


def classify_risk(risk_index: float | None) -> str | None:
    """
    Classify a HydroGuard Risk Index into a risk category.

    Bands:
        0-24.99   -> Low
        25-49.99  -> Moderate
        50-74.99  -> High
        75-100    -> Very High
    """
    if risk_index is None:
        return None

    if not 0 <= risk_index <= 100:
        raise ValueError("risk_index must be between 0 and 100")

    if risk_index < 25:
        return "Low"

    if risk_index < 50:
        return "Moderate"

    if risk_index < 75:
        return "High"

    return "Very High"
