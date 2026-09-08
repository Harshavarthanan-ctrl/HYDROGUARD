from unittest.mock import MagicMock, patch

from backend.app.risk_refresh import refresh_all_risk_data


@patch("backend.app.risk_refresh.refresh_ward_risk_scores")
@patch("backend.app.risk_refresh.refresh_ward_risk_features")
@patch("backend.app.risk_refresh.refresh_ward_weather_features")
def test_refresh_all_risk_data(
    mock_weather,
    mock_features,
    mock_scores,
):
    mock_weather.return_value = 200
    mock_features.return_value = 200
    mock_scores.return_value = 200

    result = refresh_all_risk_data()

    assert result == {
        "weather_features": 200,
        "risk_features": 200,
        "risk_scores": 200,
    }

    mock_weather.assert_called_once()
    mock_features.assert_called_once()
    mock_scores.assert_called_once()