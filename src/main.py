from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging
from typing import Dict, Any

# Import local modules - using absolute imports
from src.models import OptimizationRequest, OptimizationResult, ErrorResponse
from src.optimizer import LoadOptimizer


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_ORDERS = 25

# Global optimizer instance
optimizer = LoadOptimizer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Load Optimizer Service")
    yield
    # Shutdown
    logger.info("Shutting down Load Optimizer Service")

app = FastAPI(
    title="SmartLoad Optimization API",
    description="Optimal truck load planning service for logistics platform",
    version="1.0.0",
    lifespan=lifespan
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message="Invalid input data",
            details={"errors": exc.errors()}
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            message=str(exc.detail),
            details={}
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={}
        ).dict()
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "SmartLoad Optimization API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/v1/load-optimizer/optimize": "Optimize truck load",
            "GET /health": "Health check"
        }
    }

# Main optimization endpoint
@app.post(
    "/api/v1/load-optimizer/optimize",
    response_model=OptimizationResult,
    responses={
        200: {"description": "Optimization successful"},
        400: {"description": "Invalid input"},
        413: {"description": "Too many orders"},
        422: {"description": "Unprocessable entity"}
    },
    tags=["Optimization"]
)
async def optimize_load(request: OptimizationRequest) -> OptimizationResult:
    """
    Optimize truck load by selecting the best combination of orders.
    
    - **Maximizes**: Total payout to carrier (in cents)
    - **Constraints**: Weight, volume, hazmat compatibility, route compatibility
    - **Input**: Up to 25 orders
    - **Returns**: Optimal order combination with utilization metrics
    """
    start_time = time.time()
    
    # Validate order count
    if len(request.orders) > MAX_ORDERS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Maximum {MAX_ORDERS} orders allowed"
        )
    
    logger.info(f"Processing optimization for truck {request.truck.id} with {len(request.orders)} orders")
    
    try:
        # Run optimization
        result = optimizer.optimize_bruteforce(request.truck, request.orders)
        
        # Log performance
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Optimization completed in {elapsed_ms:.2f}ms. "
                   f"Selected {len(result.selected_order_ids)} orders, "
                   f"Revenue: ${result.total_payout_cents/100:.2f}")
        
        return result
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )

# Middleware for logging and request validation
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Check content length for large payloads
    if request.method == "POST" and request.url.path == "/api/v1/load-optimizer/optimize":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content=ErrorResponse(
                    error="PAYLOAD_TOO_LARGE",
                    message="Request payload too large",
                    details={"max_size": "1MB"}
                ).dict()
            )
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} completed in {process_time:.2f}ms")
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)