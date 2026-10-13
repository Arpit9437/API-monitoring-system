from celery import Celery
from celery.schedules import schedule

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "api_monitoring",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "dispatch-due-checks": {
        "task": "app.tasks.dispatch_due_checks",
        "schedule": schedule(run_every=settings.scheduler_interval_seconds),
    }
}
