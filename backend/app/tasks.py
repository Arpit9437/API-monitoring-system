import logging

from app.celery_app import celery_app
from app.database import SessionLocal
from app.events import publish_check_event
from app.locks import acquire_check_lock, release_check_lock
from app.schemas import CheckEvent, CheckRead
from app.services.check_service import perform_http_check, record_check
from app.services.monitor_service import get_monitor, monitors_due_for_check

logger = logging.getLogger(__name__)

RETRY_COUNTDOWN_SECONDS = 5
LOCK_TTL_SAFETY_MARGIN_SECONDS = 30


def _lock_ttl_for(timeout_seconds: int, max_retries: int) -> int:
    attempts = max_retries + 1
    return attempts * timeout_seconds + max_retries * RETRY_COUNTDOWN_SECONDS + LOCK_TTL_SAFETY_MARGIN_SECONDS


@celery_app.task(name="app.tasks.dispatch_due_checks")
def dispatch_due_checks() -> int:
    db = SessionLocal()
    try:
        due_monitors = monitors_due_for_check(db)
        for monitor in due_monitors:
            run_monitor_check.delay(monitor.id)
        return len(due_monitors)
    finally:
        db.close()


@celery_app.task(name="app.tasks.run_monitor_check", bind=True, max_retries=2)
def run_monitor_check(self, monitor_id: int) -> None:
    is_retry = self.request.retries > 0

    db = SessionLocal()
    release_lock = False
    try:
        monitor = get_monitor(db, monitor_id)
        if monitor is None:
            logger.warning("monitor %s nao encontrado, ignorando checagem", monitor_id)
            return

        if not is_retry:
            lock_ttl = _lock_ttl_for(monitor.timeout_seconds, self.max_retries)
            if not acquire_check_lock(monitor_id, lock_ttl):
                logger.info("checagem do monitor %s ja em andamento, ignorando", monitor_id)
                return
        release_lock = True

        try:
            outcome = perform_http_check(monitor)
            check = record_check(db, monitor, outcome)
        except Exception as exc:
            logger.exception("falha ao checar monitor %s", monitor_id)
            if self.request.retries < self.max_retries:
                release_lock = False
            raise self.retry(exc=exc, countdown=RETRY_COUNTDOWN_SECONDS) from exc

        event = CheckEvent(
            monitor_id=monitor.id,
            monitor_name=monitor.name,
            status=monitor.status,
            check=CheckRead.model_validate(check),
        )
        try:
            publish_check_event(event)
        except Exception:
            logger.exception("falha ao publicar evento do monitor %s", monitor_id)
    finally:
        db.close()
        if release_lock:
            release_check_lock(monitor_id)
