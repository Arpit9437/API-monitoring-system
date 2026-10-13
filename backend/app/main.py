import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.pubsub_listener import listen_for_check_events
from app.routers import checks, health, incidents, monitors, websocket

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    listener_task = asyncio.create_task(listen_for_check_events())
    yield
    listener_task.cancel()
    await asyncio.gather(listener_task, return_exceptions=True)


app = FastAPI(title="API Monitoring System", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(monitors.router)
app.include_router(checks.router)
app.include_router(incidents.router)
app.include_router(websocket.router)
