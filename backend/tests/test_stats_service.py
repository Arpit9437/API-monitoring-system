from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Check, HttpMethod, Monitor
from app.services.stats_service import compute_monitor_stats


def make_monitor(db_session: Session) -> Monitor:
    monitor = Monitor(
        name="Servico teste",
        url="https://example.com/health",
        method=HttpMethod.GET,
    )
    db_session.add(monitor)
    db_session.commit()
    db_session.refresh(monitor)
    return monitor


def add_check(db_session: Session, monitor: Monitor, *, success: bool, response_time_ms: float, age_hours: float):
    checked_at = datetime.now(timezone.utc) - timedelta(hours=age_hours)
    check = Check(
        monitor_id=monitor.id,
        success=success,
        status_code=200 if success else 500,
        response_time_ms=response_time_ms,
        checked_at=checked_at,
    )
    db_session.add(check)
    db_session.commit()


def test_compute_stats_with_mixed_results(db_session: Session):
    monitor = make_monitor(db_session)
    add_check(db_session, monitor, success=True, response_time_ms=100, age_hours=1)
    add_check(db_session, monitor, success=True, response_time_ms=200, age_hours=2)
    add_check(db_session, monitor, success=False, response_time_ms=50, age_hours=3)

    stats = compute_monitor_stats(db_session, monitor.id, window_hours=24)

    assert stats.total_checks == 3
    assert stats.successful_checks == 2
    assert round(stats.uptime_percentage, 2) == 66.67
    assert stats.average_response_time_ms == round((100 + 200 + 50) / 3, 2)


def test_compute_stats_reports_zero_average_as_zero_not_null(db_session: Session):
    monitor = make_monitor(db_session)
    add_check(db_session, monitor, success=True, response_time_ms=0, age_hours=1)
    add_check(db_session, monitor, success=True, response_time_ms=0, age_hours=2)

    stats = compute_monitor_stats(db_session, monitor.id, window_hours=24)

    assert stats.total_checks == 2
    assert stats.average_response_time_ms == 0.0


def test_compute_stats_ignores_checks_outside_window(db_session: Session):
    monitor = make_monitor(db_session)
    add_check(db_session, monitor, success=True, response_time_ms=100, age_hours=1)
    add_check(db_session, monitor, success=False, response_time_ms=100, age_hours=48)

    stats = compute_monitor_stats(db_session, monitor.id, window_hours=24)

    assert stats.total_checks == 1
    assert stats.uptime_percentage == 100.0


def test_compute_stats_with_no_checks_reports_full_uptime(db_session: Session):
    monitor = make_monitor(db_session)

    stats = compute_monitor_stats(db_session, monitor.id, window_hours=24)

    assert stats.total_checks == 0
    assert stats.uptime_percentage == 100.0
    assert stats.average_response_time_ms is None
