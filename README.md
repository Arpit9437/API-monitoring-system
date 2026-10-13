# Distributed API Health Monitoring

A real-time API monitoring platform that tracks endpoint availability, records response times, manages incidents, and displays service health through a live dashboard.

The project uses asynchronous background workers to perform scheduled HTTP health checks without blocking API requests. Users can register endpoints, configure monitoring intervals, inspect historical results, and track service outages and recoveries through a real-time dashboard.

## Features

- Configurable Monitoring: Register HTTP endpoints and configure individual health-check intervals.
- Asynchronous Processing: Execute health checks using Celery workers independently of API request handling.
- Database-Driven Scheduling: Query PostgreSQL to identify monitors that are due for their next check.
- Automatic Incident Management: Create incidents when endpoints become unavailable and resolve them after recovery.
- Real-Time Dashboard: Stream monitoring updates to connected clients using WebSockets and Redis Pub/Sub.
- Concurrency Protection: Use Redis-based locks to prevent overlapping checks for the same monitor, including during retry attempts.
- Uptime Analytics: Store check history and response times for uptime calculations and performance charts.
- Containerized Setup: Run the application and its supporting services using Docker Compose.

## Tech Stack

| Technology | Purpose |
| --- | --- |
| Python | Backend programming |
| FastAPI | REST API and WebSocket endpoints |
| SQLAlchemy 2 | Database ORM |
| PostgreSQL | Persistent storage |
| Alembic | Database migrations |
| Celery | Background task execution |
| Celery Beat | Periodic task scheduling |
| Redis | Task broker, Pub/Sub, and distributed locks |
| React | Frontend interface |
| JavaScript | Frontend development |
| Vite | Frontend development server |
| Recharts | Data visualization |
| Docker Compose | Multi-service development environment |
| Pytest | Automated testing |

## Architecture

The application separates API handling, task scheduling, health-check execution, and real-time event delivery into independent components.

```text
                 +----------------------+
                 |    React Dashboard   |
                 +----------+-----------+
                            |
                      REST / WebSocket
                            |
                 +----------v-----------+
                 |      FastAPI         |
                 +----+------------+----+
                      |            ^
                      |            | Redis Pub/Sub
                      v            |
                 +----+------------+----+
                 |        Redis         |
                 | Broker / Events /    |
                 | Distributed Locks    |
                 +----+------------+----+
                      |            ^
                      v            |
                 +----+------------+----+
                 |   Celery Workers     |
                 | HTTP Checks & Retry  |
                 +----------+-----------+
                            |
                 +----------v-----------+
                 |      PostgreSQL      |
                 | Monitors, Results,   |
                 | Incidents             |
                 +----------------------+

                 +----------------------+
                 |      Celery Beat     |
                 | Periodic Dispatcher  |
                 +----------------------+
```

### How It Works

1. Monitor Registration: The API accepts endpoint details and monitoring preferences and stores them in PostgreSQL.
2. Scheduled Discovery: Celery Beat periodically triggers a dispatcher that queries the database for monitors due for a check.
3. Background Execution: Eligible monitors are queued for Celery workers, which send HTTP requests and record the results.
4. Incident Tracking: Availability transitions trigger incident creation or resolution.
5. Live Updates: Workers publish completed check results to Redis Pub/Sub, and the API forwards these events to connected dashboard clients through WebSockets.

### Preventing Overlapping Checks

Slow or unstable endpoints can remain under evaluation when another scheduled check becomes due. Without coordination, multiple workers could check the same endpoint simultaneously and produce conflicting status updates.

PulseWatch uses a monitor-specific Redis lock acquired through `SET NX EX` before a check begins. The lock protects the check throughout its retry attempts, helping prevent concurrent execution for the same monitor.

## Project Structure

```text
backend/
├── app/
│   ├── routers/
│   │   ├── monitors.py
│   │   ├── checks.py
│   │   ├── incidents.py
│   │   └── websocket.py
│   ├── services/
│   ├── models.py
│   ├── schemas.py
│   ├── tasks.py
│   ├── celery_app.py
│   └── locks.py
├── alembic/
└── tests/

frontend/
└── src/
    ├── api/
    ├── hooks/
    ├── components/
    └── pages/
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Git

### Run with Docker Compose

1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

2. Configure environment variables

```bash
cp .env.example .env
```

Update `.env` if your local ports or service connection settings differ from the defaults.

3. Build and start the services

```bash
docker compose up --build
```

### Application URLs

| Service | URL |
| --- | --- |
| Frontend Dashboard | http://localhost:5174 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| PostgreSQL | localhost:5433 |
| Redis | localhost:6379 |

The ports can be customized through the corresponding environment variables.

## Local Development

### Backend Setup

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
```

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

Start the Celery worker in a separate terminal:

```bash
cd backend
source .venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

Start Celery Beat in another terminal:

```bash
cd backend
source .venv/bin/activate
celery -A app.celery_app beat --loglevel=info
```

Ensure PostgreSQL and Redis are running and that the environment variables point to the correct services.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Testing

Run the backend test suite:

```bash
cd backend
source .venv/bin/activate
pytest
```

The tests use an in-memory SQLite database for database-related test cases, allowing the suite to run without a separate PostgreSQL instance.

Key test scenarios include:

- Successful HTTP checks, failed requests, and timeouts
- Incident creation and recovery transitions
- Redis lock behavior during retries
- Uptime calculations
- Monitor API operations

## Configuration

The primary environment variables are listed below.

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection URL |
| `CELERY_BROKER_URL` | Celery message broker URL |
| `CELERY_RESULT_BACKEND` | Celery result backend configuration |
| `SCHEDULER_INTERVAL_SECONDS` | Frequency of due-monitor discovery |
| `VITE_API_URL` | Backend API URL used by the frontend |
| `VITE_WS_URL` | WebSocket URL used by the frontend |

See `.env.example` for the complete configuration.

## Engineering Highlights

- Separation of request handling and background processing
- Periodic scheduling with database-driven task discovery
- Distributed coordination using Redis locks
- Event-driven dashboard updates through WebSockets
- Automated incident lifecycle management
- Historical monitoring data and uptime analytics
- Automated tests for core business logic
- Multi-service development using Docker Compose

Note: Update the repository URL, project name, file paths, and feature descriptions to match your actual implementation. Remove any features that are not implemented or tested before publishing the repository.
