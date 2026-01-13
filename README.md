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

