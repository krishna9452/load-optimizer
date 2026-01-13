import json
import time
import requests
import random

def generate_large_test():
    """Generate test data with 22 orders"""
    orders = []
    for i in range(22):
        orders.append({
            "id": f"ord-{i:03d}",
            "payout_cents": random.randint(100000, 500000),
            "weight_lbs": random.randint(5000, 15000),
            "volume_cuft": random.randint(200, 800),
            "origin": "Los Angeles, CA",
            "destination": "Dallas, TX",
            "pickup_date": "2025-12-05",
            "delivery_date": "2025-12-09",
            "is_hazmat": random.choice([True, False])
        })
    
    request_data = {
        "truck": {
            "id": "truck-123",
            "max_weight_lbs": 44000,
            "max_volume_cuft": 3000
        },
        "orders": orders
    }
    
    return request_data

def test_performance():
    url = "http://localhost:8080/api/v1/load-optimizer/optimize"
    
    # Test with 22 orders
    print("Testing with 22 orders...")
    data = generate_large_test()
    
    start_time = time.time()
    response = requests.post(url, json=data)
    elapsed_ms = (time.time() - start_time) * 1000
    
    print(f"Response time: {elapsed_ms:.2f}ms")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Selected {len(result['selected_order_ids'])} orders")
        print(f"Total payout: ${result['total_payout_cents']/100:.2f}")
        print(f"Performance: {'✓ PASS' if elapsed_ms < 800 else '✗ FAIL'} (<800ms requirement)")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_performance()
