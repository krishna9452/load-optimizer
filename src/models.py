from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import date


# -------------------------
# Core Domain Models
# -------------------------

class Truck(BaseModel):
    id: str
    max_weight_lbs: int = Field(..., gt=0)
    max_volume_cuft: int = Field(..., gt=0)


class Order(BaseModel):
    id: str
    payout_cents: int = Field(..., ge=0)
    weight_lbs: int = Field(..., gt=0)
    volume_cuft: int = Field(..., gt=0)

    origin: str
    destination: str

    pickup_date: date
    delivery_date: date

    is_hazmat: bool

    class Config:
        json_schema_extra = {
            "example": {
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
        }


# -------------------------
# API Request / Response
# -------------------------

class OptimizationRequest(BaseModel):
    truck: Truck
    orders: List[Order]


class OptimizationResult(BaseModel):
    truck_id: str
    selected_order_ids: List[str]

    total_payout_cents: int
    total_weight_lbs: int
    total_volume_cuft: int

    utilization_weight_percent: float
    utilization_volume_percent: float


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Dict
