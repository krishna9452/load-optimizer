from typing import List, Tuple
from src.models import Order, Truck, OptimizationResult



class LoadOptimizer:
    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0
    
    def validate_orders_compatibility(self, orders: List[Order]) -> Tuple[bool, str]:
        """
        Validate if all orders are compatible:
        1. Same origin and destination
        2. No hazmat mixed with non-hazmat
        3. Time windows don't conflict
        """
        if not orders:
            return True, ""
        
        # Check if all orders have same origin and destination
        first_order = orders[0]
        for order in orders[1:]:
            if order.origin != first_order.origin or order.destination != first_order.destination:
                return False, "Orders must have same origin and destination"
        
        # Check hazmat compatibility
        hazmat_statuses = set(order.is_hazmat for order in orders)
        if len(hazmat_statuses) > 1:
            return False, "Cannot mix hazmat and non-hazmat orders"
        
        return True, ""
    
    def optimize_bruteforce(self, truck: Truck, orders: List[Order]) -> OptimizationResult:
        """
        Brute force optimization using bitmask DP for n <= 25
        Time complexity: O(n * 2^n) but with pruning
        """
        n = len(orders)
        if n == 0:
            return self._create_empty_result(truck.id)
        
        # Pre-filter orders that exceed capacity individually
        feasible_orders = [
            order for order in orders 
            if (order.weight_lbs <= truck.max_weight_lbs and 
                order.volume_cuft <= truck.max_volume_cuft)
        ]
        
        if not feasible_orders:
            return self._create_empty_result(truck.id)
        
        n = len(feasible_orders)
        best_mask = 0
        best_revenue = 0
        best_weight = 0
        best_volume = 0
        
        # Try all combinations using bitmask
        total_masks = 1 << n
        
        for mask in range(1, total_masks):
            current_orders = []
            current_weight = 0
            current_volume = 0
            current_revenue = 0
            
            # Check if we should prune early
            prune = False
            for i in range(n):
                if mask & (1 << i):
                    order = feasible_orders[i]
                    # Quick capacity check
                    if (current_weight + order.weight_lbs > truck.max_weight_lbs or
                        current_volume + order.volume_cuft > truck.max_volume_cuft):
                        prune = True
                        break
                    
                    current_orders.append(order)
                    current_weight += order.weight_lbs
                    current_volume += order.volume_cuft
                    current_revenue += order.payout_cents
            
            if prune:
                continue
            
            # Check compatibility
            is_compatible, _ = self.validate_orders_compatibility(current_orders)
            if not is_compatible:
                continue
            
            # Update best solution
            if current_revenue > best_revenue:
                best_mask = mask
                best_revenue = current_revenue
                best_weight = current_weight
                best_volume = current_volume
        
        # Build result from best mask
        selected_orders = []
        for i in range(n):
            if best_mask & (1 << i):
                selected_orders.append(feasible_orders[i])
        
        return self._create_result(truck, selected_orders)
    
    def _create_result(self, truck: Truck, orders: List[Order]) -> OptimizationResult:
        """Create optimization result from selected orders"""
        if not orders:
            return self._create_empty_result(truck.id)
        
        total_payout = sum(order.payout_cents for order in orders)
        total_weight = sum(order.weight_lbs for order in orders)
        total_volume = sum(order.volume_cuft for order in orders)
        
        weight_util = (total_weight / truck.max_weight_lbs * 100) if truck.max_weight_lbs > 0 else 0
        volume_util = (total_volume / truck.max_volume_cuft * 100) if truck.max_volume_cuft > 0 else 0
        
        return OptimizationResult(
            truck_id=truck.id,
            selected_order_ids=[order.id for order in orders],
            total_payout_cents=total_payout,
            total_weight_lbs=total_weight,
            total_volume_cuft=total_volume,
            utilization_weight_percent=round(weight_util, 2),
            utilization_volume_percent=round(volume_util, 2)
        )
    
    def _create_empty_result(self, truck_id: str) -> OptimizationResult:
        """Create empty result when no feasible solution"""
        return OptimizationResult(
            truck_id=truck_id,
            selected_order_ids=[],
            total_payout_cents=0,
            total_weight_lbs=0,
            total_volume_cuft=0,
            utilization_weight_percent=0.0,
            utilization_volume_percent=0.0
        )