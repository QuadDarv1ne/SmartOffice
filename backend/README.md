# SmartOffice Backend

FastAPI backend for SmartOffice system.

## Setup

### Using Docker
```bash
docker build -t smartoffice-backend .
docker run -p 8000:8000 smartoffice-backend
```

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/smartoffice"

# Run server
uvicorn app.main:app --reload --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql+asyncpg://postgres:postgres@localhost:5432/smartoffice |
| SECRET_KEY | JWT secret key | (change in production) |
| DEBUG | Enable debug mode | True |
