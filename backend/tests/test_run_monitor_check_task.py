from datetime import datetime, timezone
from unittest.mock import MagicMock

from app import tasks
from app.models import Check, HttpMethod, Monitor, MonitorStatus
from app.services.check_service import CheckOutcome


def make_monitor() -> Monitor:
    return Monitor(
        id=1,
        name="servico",
        url="https://example.com",
        method=HttpMethod.GET,
        timeout_seconds=5,
        status=MonitorStatus.UNKNOWN,
    )


def test_run_monitor_check_holds_lock_across_retries(monkeypatch):
    monitor = make_monitor()

    monkeypatch.setattr(tasks, "SessionLocal", MagicMock(return_value=MagicMock(close=MagicMock())))
    monkeypatch.setattr(tasks, "RETRY_COUNTDOWN_SECONDS", 0)
    monkeypatch.setattr(tasks, "get_monitor", lambda db, monitor_id: monitor)
    monkeypatch.setattr(tasks, "perform_http_check", lambda m: CheckOutcome(True, 200, 10.0, None))
    monkeypatch.setattr(tasks, "publish_check_event", MagicMock())

    acquire_mock = MagicMock(return_value=True)
    release_mock = MagicMock()
    monkeypatch.setattr(tasks, "acquire_check_lock", acquire_mock)
    monkeypatch.setattr(tasks, "release_check_lock", release_mock)

    attempts = {"count": 0}

    def flaky_record_check(db, monitor_arg, outcome):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("falha transiente de banco")
        return Check(
            id=1,
            monitor_id=monitor_arg.id,
            success=True,
            status_code=200,
            response_time_ms=10.0,
            error_message=None,
            checked_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(tasks, "record_check", flaky_record_check)

    tasks.run_monitor_check.apply(args=[1])

    assert attempts["count"] == 3
    assert acquire_mock.call_count == 1
    assert release_mock.call_count == 1


def test_run_monitor_check_releases_lock_once_after_success(monkeypatch):
    monitor = make_monitor()

    monkeypatch.setattr(tasks, "SessionLocal", MagicMock(return_value=MagicMock(close=MagicMock())))
    monkeypatch.setattr(tasks, "get_monitor", lambda db, monitor_id: monitor)
    monkeypatch.setattr(tasks, "perform_http_check", lambda m: CheckOutcome(True, 200, 10.0, None))
    monkeypatch.setattr(tasks, "publish_check_event", MagicMock())

    acquire_mock = MagicMock(return_value=True)
    release_mock = MagicMock()
    monkeypatch.setattr(tasks, "acquire_check_lock", acquire_mock)
    monkeypatch.setattr(tasks, "release_check_lock", release_mock)

    monkeypatch.setattr(
        tasks,
        "record_check",
        lambda db, monitor_arg, outcome: Check(
            id=1,
            monitor_id=monitor_arg.id,
            success=True,
            status_code=200,
            response_time_ms=10.0,
            error_message=None,
            checked_at=datetime.now(timezone.utc),
        ),
    )

    tasks.run_monitor_check.apply(args=[1])

    assert acquire_mock.call_count == 1
    assert release_mock.call_count == 1


def test_run_monitor_check_skips_when_lock_held(monkeypatch):
    monitor = make_monitor()

    monkeypatch.setattr(tasks, "SessionLocal", MagicMock(return_value=MagicMock(close=MagicMock())))
    monkeypatch.setattr(tasks, "get_monitor", lambda db, monitor_id: monitor)
    monkeypatch.setattr(tasks, "acquire_check_lock", MagicMock(return_value=False))
    release_mock = MagicMock()
    monkeypatch.setattr(tasks, "release_check_lock", release_mock)
    perform_check_mock = MagicMock()
    monkeypatch.setattr(tasks, "perform_http_check", perform_check_mock)

    tasks.run_monitor_check.apply(args=[1])

    perform_check_mock.assert_not_called()
    release_mock.assert_not_called()
