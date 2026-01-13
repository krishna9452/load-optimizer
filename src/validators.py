from typing import List, Tuple
from datetime import date

# Fixed: Use absolute imports
from src.models import Order
from constants import ErrorMessages


def validate_orders_compatibility(orders: List[Order]) -> Tuple[bool, str]:
    """
    Validate if all orders are compatible:
    1. Same origin and destination
    2. No hazmat mixed with non-hazmat
    3. Time windows don't conflict (pickup ≤ delivery for all, no overlapping conflicts)
    """
    if not orders:
        return True, ""
    
    # Check if all orders have same origin and destination
    first_order = orders[0]
    for order in orders[1:]:
        if order.origin != first_order.origin or order.destination != first_order.destination:
            return False, ErrorMessages.ROUTE_CONFLICT
    
    # Check hazmat compatibility
    hazmat_statuses = set(order.is_hazmat for order in orders)
    if len(hazmat_statuses) > 1:
        return False, ErrorMessages.HAZMAT_CONFLICT
    
    # Check time windows - simplified: ensure all can be served in sequence
    # Get overall pickup and delivery windows
    min_pickup = min(order.pickup_date for order in orders)
    max_delivery = max(order.delivery_date for order in orders)
    
    # Check if any order has impossible time window for the truck route
    for order in orders:
        if order.delivery_date < order.pickup_date:
            return False, "Order has invalid time window"
    
    # For simplicity, assume truck can handle multiple stops within these windows
    # In real implementation, you'd check actual route timing
    if (max_delivery - min_pickup).days > 30:
        return False, "Time window too wide for combined delivery"
    
    return True, ""


def validate_capacity(truck: Truck, orders: List[Order]) -> bool:
    """Validate if orders fit in truck capacity"""
    total_weight = sum(order.weight_lbs for order in orders)
    total_volume = sum(order.volume_cuft for order in orders)
    
    return (total_weight <= truck.max_weight_lbs and 
            total_volume <= truck.max_volume_cuft)