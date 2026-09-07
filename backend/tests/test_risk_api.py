from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ward_risk_endpoint():
    response = client.get("/api/v1/risk/wards")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 200
    assert len(data["wards"]) == 200


def test_ward_risk_response_structure():
    response = client.get("/api/v1/risk/wards")

    data = response.json()
    ward = data["wards"][0]

    assert "ward" in ward
    assert "zone" in ward
    assert "weather_hazard" in ward
    assert "drainage_vulnerability" in ward
    assert "hydroguard_risk_index" in ward
    assert "risk_category" in ward
    assert "weather_data_available" in ward
    assert "drainage_data_available" in ward


def test_missing_drainage_wards_have_null_risk():
    response = client.get("/api/v1/risk/wards")

    wards = response.json()["wards"]

    missing_drainage = [
        ward
        for ward in wards
        if not ward["drainage_data_available"]
    ]

    assert len(missing_drainage) == 2

    for ward in missing_drainage:
        assert ward["hydroguard_risk_index"] is None
        assert ward["risk_category"] is None
def test_individual_ward_risk():
    response = client.get("/api/v1/risk/wards/085")

    assert response.status_code == 200

    data = response.json()

    assert data["ward"] == "085"
    assert data["zone"] == "7"
    assert data["weather_hazard"] == 0.0
    assert data["drainage_data_available"] is True
    assert data["hydroguard_risk_index"] == 21.12
    assert data["risk_category"] == "Low"


def test_missing_ward_returns_404():
    response = client.get("/api/v1/risk/wards/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ward 999 not found"


def test_ward_without_drainage_data():
    response = client.get("/api/v1/risk/wards/003")

    assert response.status_code == 200

    data = response.json()

    assert data["ward"] == "003"
    assert data["weather_data_available"] is True
    assert data["drainage_data_available"] is False
    assert data["drainage_vulnerability"] is None
    assert data["hydroguard_risk_index"] is None
    assert data["risk_category"] is None