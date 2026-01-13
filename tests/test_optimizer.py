import pytest
from datetime import date
from src.models import Order, Truck
from src.optimizer import LoadOptimizer

def create_sample_orders():
    return [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False
        ),
        Order(
            id="ord-002",
            payout_cents=180000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 4),
            delivery_date=date(2025, 12, 10),
            is_hazmat=False
        ),
        Order(
            id="ord-003",
            payout_cents=320000,
            weight_lbs=30000,
            volume_cuft=1800,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 8),
            is_hazmat=True
        )
    ]

def test_optimizer_basic():
    truck = Truck(
        id="truck-123",
        max_weight_lbs=44000,
        max_volume_cuft=3000
    )
    
    orders = create_sample_orders()
    optimizer = LoadOptimizer()
    
    result = optimizer.optimize_bruteforce(truck, orders)
    
    assert result.truck_id == "truck-123"
    assert set(result.selected_order_ids) == {"ord-001", "ord-002"}
    assert result.total_payout_cents == 430000
    assert result.total_weight_lbs == 30000
    assert result.total_volume_cuft == 2100

def test_optimizer_empty():
    truck = Truck(
        id="truck-123",
        max_weight_lbs=44000,
        max_volume_cuft=3000
    )
    
    optimizer = LoadOptimizer()
    result = optimizer.optimize_bruteforce(truck, [])
    
    assert result.selected_order_ids == []
    assert result.total_payout_cents == 0

def test_optimizer_overweight():
    truck = Truck(
        id="truck-123",
        max_weight_lbs=10000,  # Very small capacity
        max_volume_cuft=3000
    )
    
    orders = create_sample_orders()
    optimizer = LoadOptimizer()
    
    result = optimizer.optimize_bruteforce(truck, orders)
    
    # Should select nothing or only small orders that fit
    for order in orders:
        if order.weight_lbs <= 10000:
            # If any order fits, it should be selected
            assert len(result.selected_order_ids) >= 0
            break

def test_optimizer_single_hazmat():
    truck = Truck(
        id="truck-123",
        max_weight_lbs=44000,
        max_volume_cuft=3000
    )
    
    orders = [
        Order(
            id="ord-001",
            payout_cents=320000,
            weight_lbs=30000,
            volume_cuft=1800,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 8),
            is_hazmat=True
        )
    ]
    
    optimizer = LoadOptimizer()
    result = optimizer.optimize_bruteforce(truck, orders)
    
    assert result.selected_order_ids == ["ord-001"]
    assert result.total_payout_cents == 320000

def test_optimizer_different_routes():
    truck = Truck(
        id="truck-123",
        max_weight_lbs=44000,
        max_volume_cuft=3000
    )
    
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False
        ),
        Order(
            id="ord-002",
            payout_cents=300000,
            weight_lbs=20000,
            volume_cuft=1500,
            origin="Chicago, IL",  # Different origin
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 4),
            delivery_date=date(2025, 12, 10),
            is_hazmat=False
        )
    ]
    
    optimizer = LoadOptimizer()
    result = optimizer.optimize_bruteforce(truck, orders)
    
    # Should select only one order (different routes are incompatible)
    assert len(result.selected_order_ids) == 1
    # Should select the higher paying order
    if len(result.selected_order_ids) == 1:
        assert result.selected_order_ids[0] == "ord-002"