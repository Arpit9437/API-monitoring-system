from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Monitor
from app.schemas import MonitorCreate, MonitorUpdate


def list_monitors(db: Session) -> list[Monitor]:
    return list(db.scalars(select(Monitor).order_by(Monitor.created_at)))


def get_monitor(db: Session, monitor_id: int) -> Monitor | None:
    return db.get(Monitor, monitor_id)


def get_monitor_or_404(db: Session, monitor_id: int) -> Monitor:
    monitor = get_monitor(db, monitor_id)
    if monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="monitor nao encontrado")
    return monitor


def create_monitor(db: Session, data: MonitorCreate) -> Monitor:
    monitor = Monitor(
        name=data.name,
        url=str(data.url),
        method=data.method,
        expected_status=data.expected_status,
        interval_seconds=data.interval_seconds,
        timeout_seconds=data.timeout_seconds,
        is_active=data.is_active,
    )
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


def update_monitor(db: Session, monitor: Monitor, data: MonitorUpdate) -> Monitor:
    updates = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in updates.items():
        setattr(monitor, field, str(value) if field == "url" else value)
    db.commit()
    db.refresh(monitor)
    return monitor


def delete_monitor(db: Session, monitor: Monitor) -> None:
    db.delete(monitor)
    db.commit()


def monitors_due_for_check(db: Session) -> list[Monitor]:
    monitors = db.scalars(select(Monitor).where(Monitor.is_active.is_(True)))
    due = []
    for monitor in monitors:
        if monitor.last_checked_at is None:
            due.append(monitor)
            continue
        elapsed = _seconds_since(monitor.last_checked_at)
        if elapsed >= monitor.interval_seconds:
            due.append(monitor)
    return due


def _seconds_since(moment: datetime) -> float:
    now = datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return (now - moment).total_seconds()
