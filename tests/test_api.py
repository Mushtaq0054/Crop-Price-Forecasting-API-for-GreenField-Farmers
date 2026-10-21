"""
Automated Test Suite for Crop Price Forecasting FastAPI Service
Client: GreenField Farmers Co-op
Project: Crop Price Forecasting API for GreenField Farmers
Task 4: Unit and integration tests for valid and invalid inputs using Pytest.
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app, load_model_and_reference_data

# Initialize TestClient
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_model():
    """Ensure model and reference data are loaded before running tests."""
    load_model_and_reference_data()


# -------------------------------------------------------------
# 1. HEALTH AND STATUS TESTS
# -------------------------------------------------------------
def test_root_endpoint():
    """Verify root GET endpoint returns 200 and API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "GreenField Farmers Co-op" in data["service"]
    assert "Wheat" in data["supported_crops"]


def test_health_endpoint():
    """Verify health GET endpoint confirms model is loaded."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "supported_crops" in data


# -------------------------------------------------------------
# 2. VALID PREDICTION TESTS
# -------------------------------------------------------------
def test_predict_valid_wheat():
    """Verify valid prediction request for Wheat."""
    payload = {
        "crop": "Wheat",
        "date": "2026-10-25"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["crop"] == "Wheat"
    assert data["target_date"] == "2026-10-25"
    assert isinstance(data["predicted_next_week_price_pkr"], (int, float))
    assert data["predicted_next_week_price_pkr"] > 0
    assert "confidence_interval_pkr" in data
    assert data["confidence_interval_pkr"]["lower_bound"] < data["confidence_interval_pkr"]["upper_bound"]
    assert data["currency"] == "PKR per Quintal"


def test_predict_valid_rice():
    """Verify valid prediction request for Rice."""
    payload = {
        "crop": "Rice",
        "date": "2026-11-15"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "Rice"
    assert data["predicted_next_week_price_pkr"] > 0


def test_predict_valid_potato():
    """Verify valid prediction request for Potato."""
    payload = {
        "crop": "Potato",
        "date": "2026-12-05"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "Potato"
    assert data["predicted_next_week_price_pkr"] > 0


def test_predict_case_insensitive_crop():
    """Verify that lowercase crop names (e.g. 'wheat', 'rice') are accepted."""
    payload = {
        "crop": "wheat",
        "date": "2026-10-25"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "Wheat"


def test_predict_with_real_time_context():
    """Verify prediction with full optional market and weather attributes."""
    payload = {
        "crop": "Wheat",
        "date": "2026-10-25",
        "current_price_pkr": 3820.0,
        "market_arrival_tonnes": 420.0,
        "rainfall_mm": 12.5,
        "temperature_c": 26.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_next_week_price_pkr"] > 0


# -------------------------------------------------------------
# 3. INVALID INPUT & ERROR HANDLING TESTS
# -------------------------------------------------------------
def test_predict_invalid_crop():
    """Verify that unsupported crop types return validation error."""
    payload = {
        "crop": "Mango",
        "date": "2026-10-25"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "Unsupported crop" in str(data)


def test_predict_invalid_date_format():
    """Verify that malformed date strings return validation error."""
    payload = {
        "crop": "Wheat",
        "date": "25-10-2026"  # DD-MM-YYYY instead of YYYY-MM-DD
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "Invalid date format" in str(data)


def test_predict_non_date_string():
    """Verify that non-date text returns validation error."""
    payload = {
        "crop": "Wheat",
        "date": "tomorrow"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_missing_crop():
    """Verify that missing 'crop' field returns 422 Unprocessable Entity."""
    payload = {
        "date": "2026-10-25"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_missing_date():
    """Verify that missing 'date' field returns 422 Unprocessable Entity."""
    payload = {
        "crop": "Wheat"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_empty_payload():
    """Verify that an empty JSON body returns 422 validation error."""
    response = client.post("/predict", json={})
    assert response.status_code == 422
