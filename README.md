# SmartLoad Optimization API

A high-performance REST API for optimal truck load planning in logistics platforms. The service selects the best combination of orders to maximize carrier payout while respecting weight, volume, hazmat, and route compatibility constraints.

## 🚀 Features

- **Optimal Load Planning**: Uses bitmask dynamic programming for up to 25 orders
- **Multiple Constraints**: Respects weight, volume, hazmat compatibility, route compatibility, and time windows
- **High Performance**: Processes 25 orders in under 800ms
- **Production Ready**: Input validation, error handling, logging, and health checks
- **Containerized**: Complete Docker support
- **RESTful API**: Clean, documented endpoints with proper HTTP status codes

## 🛠️ Tech Stack

- **Python 3.11** with **FastAPI** for high-performance async API
- **Pydantic** for data validation and serialization
- **Uvicorn** ASGI server
- **Docker** for containerization
- **Bitmask DP Algorithm** for optimization

## 📦 Installation & Setup

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/load-optimizer.git
cd load-optimizer

# Build and run with Docker Compose
docker-compose up --build

# The service will be available at http://localhost:8080
```

## Manual Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/load-optimizer.git
cd load-optimizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
cd src
PYTHONPATH=. uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```
## 📚 API Documentation
Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## 🔧 API Endpoints

```text
POST /api/v1/load-optimizer/optimize
```
Optimizes truck load by selecting the best combination of orders.

### Request Body:

```json
{
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
      "is_hazmat": false
    }
  ]
}
```
### Response:

```json
{
  "truck_id": "truck-123",
  "selected_order_ids": ["ord-001", "ord-002"],
  "total_payout_cents": 430000,
  "total_weight_lbs": 30000,
  "total_volume_cuft": 2100,
  "utilization_weight_percent": 68.18,
  "utilization_volume_percent": 70.0
}
```
## GET /health

Health check endpoint.

### Response:

```json
{
  "status": "healthy",
  "timestamp": 1702400000.123456
}
```
## 🧪 Testing
### Run Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v
```
### Test with cURL

```bash
# Health check
curl http://localhost:8080/health

# Sample optimization
curl -X POST http://localhost:8080/api/v1/load-optimizer/optimize \
  -H "Content-Type: application/json" \
  -d '{
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
        "is_hazmat": false
      }
    ]
  }'
```

## 🏗️ Project Structure

```text
load-optimizer/
├── Dockerfile              
├── docker-compose.yml      
├── requirements.txt        
├── sample_request.json     
├── src/                    
│   ├── __init__.py        
│   ├── main.py           
│   ├── models.py         
│   └── optimizer.py      
└── tests/                 
    ├── __init__.py
    ├── test_api.py       
    └── test_optimizer.py
```





