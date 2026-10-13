import time
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Check, Incident, Monitor, MonitorStatus


@dataclass
class CheckOutcome:
    success: bool
    status_code: int | None
    response_time_ms: float | None
    error_message: str | None


def perform_http_check(monitor: Monitor) -> CheckOutcome:
    started_at = time.monotonic()
    try:
        response = httpx.request(
            monitor.method.value,
            monitor.url,
            timeout=monitor.timeout_seconds,
            follow_redirects=True,
        )
    except httpx.RequestError as exc:
        elapsed_ms = (time.monotonic() - started_at) * 1000
        return CheckOutcome(
            success=False,
            status_code=None,
            response_time_ms=elapsed_ms,
            error_message=str(exc),
        )

    elapsed_ms = (time.monotonic() - started_at) * 1000
    success = response.status_code == monitor.expected_status
    error_message = None
    if not success:
        error_message = f"esperado status {monitor.expected_status}, recebido {response.status_code}"

    return CheckOutcome(
        success=success,
        status_code=response.status_code,
        response_time_ms=elapsed_ms,
        error_message=error_message,
    )


def record_check(db: Session, monitor: Monitor, outcome: CheckOutcome) -> Check:
    check = Check(
        monitor_id=monitor.id,
        success=outcome.success,
        status_code=outcome.status_code,
        response_time_ms=outcome.response_time_ms,
        error_message=outcome.error_message,
    )
    db.add(check)

    previous_status = monitor.status
    new_status = MonitorStatus.UP if outcome.success else MonitorStatus.DOWN
    monitor.status = new_status
    monitor.last_checked_at = datetime.now(timezone.utc)

    _sync_incident(db, monitor, previous_status, new_status, outcome)

    db.commit()
    db.refresh(check)
    return check


def _sync_incident(
    db: Session,
    monitor: Monitor,
    previous_status: MonitorStatus,
    new_status: MonitorStatus,
    outcome: CheckOutcome,
) -> None:
    if previous_status != MonitorStatus.DOWN and new_status == MonitorStatus.DOWN:
        incident = Incident(
            monitor_id=monitor.id,
            cause=outcome.error_message or "falha desconhecida",
        )
        db.add(incident)
        return

    if previous_status == MonitorStatus.DOWN and new_status == MonitorStatus.UP:
        open_incident = db.scalar(
            select(Incident)
            .where(Incident.monitor_id == monitor.id, Incident.resolved_at.is_(None))
            .order_by(Incident.started_at.desc())
        )
        if open_incident is not None:
            open_incident.resolved_at = datetime.now(timezone.utc)
