import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "endpoints" in response.json()

def test_optimize_empty_orders():
    request_data = {
        "truck": {
            "id": "truck-123",
            "max_weight_lbs": 44000,
            "max_volume_cuft": 3000
        },
        "orders": []
    }
    
    response = client.post("/api/v1/load-optimizer/optimize", json=request_data)
    assert response.status_code == 200
    result = response.json()
    assert result["selected_order_ids"] == []
    assert result["total_payout_cents"] == 0

def test_optimize_single_order():
    request_data = {
        "truck": {
            "id": "truck-123",
            "max_weight_lbs": 44000,
            "max_volume_cuft": 3000
        },
        "orders": [
            {
                "id": "ord-001",
                "payout_cents": 250000,
                "weight_lbs": 18000,
                "volume_cuft": 1200,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025-12-05",
                "delivery_date": "2025-12-09",
                "is_hazmat": False
            }
        ]
    }
    
    response = client.post("/api/v1/load-optimizer/optimize", json=request_data)
    assert response.status_code == 200
    result = response.json()
    assert result["selected_order_ids"] == ["ord-001"]
    assert result["total_payout_cents"] == 250000
    assert result["total_weight_lbs"] == 18000

def test_optimize_invalid_input():
    request_data = {
        "truck": {
            "id": "truck-123",
            "max_weight_lbs": -100,  # Invalid negative weight
            "max_volume_cuft": 3000
        },
        "orders": []
    }
    
    response = client.post("/api/v1/load-optimizer/optimize", json=request_data)
    assert response.status_code == 400

def test_optimize_too_many_orders():
    orders = []
    for i in range(30):
        orders.append({
            "id": f"ord-{i}",
            "payout_cents": 100000,
            "weight_lbs": 1000,
            "volume_cuft": 100,
            "origin": "Los Angeles, CA",
            "destination": "Dallas, TX",
            "pickup_date": "2025-12-05",
            "delivery_date": "2025-12-09",
            "is_hazmat": False
        })
    
    request_data = {
        "truck": {
            "id": "truck-123",
            "max_weight_lbs": 44000,
            "max_volume_cuft": 3000
        },
        "orders": orders
    }
    
    response = client.post("/api/v1/load-optimizer/optimize", json=request_data)
    assert response.status_code == 413

def test_hazmat_conflict():
    request_data = {
        "truck": {
            "id": "truck-123",
            "max_weight_lbs": 44000,
            "max_volume_cuft": 3000
        },
        "orders": [
            {
                "id": "ord-001",
                "payout_cents": 250000,
                "weight_lbs": 18000,
                "volume_cuft": 1200,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025-12-05",
                "delivery_date": "2025-12-09",
                "is_hazmat": False
            },
            {
                "id": "ord-002",
                "payout_cents": 320000,
                "weight_lbs": 20000,
                "volume_cuft": 1500,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025-12-06",
                "delivery_date": "2025-12-08",
                "is_hazmat": True
            }
        ]
    }
    
    response = client.post("/api/v1/load-optimizer/optimize", json=request_data)
    assert response.status_code == 200
    # Should select only one order (not both since hazmat conflicts)
    result = response.json()
    assert len(result["selected_order_ids"]) == 1