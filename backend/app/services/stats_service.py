from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Check
from app.schemas import MonitorStats


def compute_monitor_stats(db: Session, monitor_id: int, window_hours: int = 24) -> MonitorStats:
    since = datetime.now(timezone.utc) - timedelta(hours=window_hours)

    total_checks = _count_checks(db, monitor_id, since)
    successful_checks = _count_checks(db, monitor_id, since, success=True)
    average_response_time_ms = db.scalar(
        select(func.avg(Check.response_time_ms)).where(
            Check.monitor_id == monitor_id, Check.checked_at >= since
        )
    )

    uptime_percentage = 100.0
    if total_checks > 0:
        uptime_percentage = round((successful_checks / total_checks) * 100, 2)

    return MonitorStats(
        monitor_id=monitor_id,
        window_hours=window_hours,
        total_checks=total_checks,
        successful_checks=successful_checks,
        uptime_percentage=uptime_percentage,
        average_response_time_ms=(
            round(average_response_time_ms, 2) if average_response_time_ms is not None else None
        ),
    )


def _count_checks(db: Session, monitor_id: int, since: datetime, success: bool | None = None) -> int:
    conditions = [Check.monitor_id == monitor_id, Check.checked_at >= since]
    if success is not None:
        conditions.append(Check.success.is_(success))
    return db.scalar(select(func.count(Check.id)).where(*conditions)) or 0
