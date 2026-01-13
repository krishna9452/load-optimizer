from enum import Enum

class ErrorMessages(str, Enum):
    INVALID_INPUT = "Invalid input data"
    NO_FEASIBLE_SOLUTION = "No feasible combination found"
    PAYLOAD_TOO_LARGE = "Too many orders (max 25 allowed)"
    TIME_WINDOW_CONFLICT = "Orders have conflicting time windows"
    HAZMAT_CONFLICT = "Cannot mix hazmat and non-hazmat orders"
    ROUTE_CONFLICT = "Orders must have same origin and destination"

MAX_ORDERS = 25  # Conservative limit for DP
MAX_TIME_WINDOW_GAP_DAYS = 30
CACHE_SIZE = 1000