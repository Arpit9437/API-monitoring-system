import httpx
import respx
from sqlalchemy.orm import Session

from app.models import HttpMethod, Incident, Monitor, MonitorStatus
from app.services.check_service import perform_http_check, record_check


def make_monitor(db_session: Session, **overrides) -> Monitor:
    monitor = Monitor(
        name="Servico teste",
        url="https://example.com/health",
        method=HttpMethod.GET,
        expected_status=200,
        interval_seconds=60,
        timeout_seconds=5,
        **overrides,
    )
    db_session.add(monitor)
    db_session.commit()
    db_session.refresh(monitor)
    return monitor


@respx.mock
def test_perform_http_check_success(db_session: Session):
    monitor = make_monitor(db_session)
    respx.get(monitor.url).mock(return_value=httpx.Response(200))

    outcome = perform_http_check(monitor)

    assert outcome.success is True
    assert outcome.status_code == 200
    assert outcome.error_message is None
    assert outcome.response_time_ms is not None


@respx.mock
def test_perform_http_check_unexpected_status(db_session: Session):
    monitor = make_monitor(db_session)
    respx.get(monitor.url).mock(return_value=httpx.Response(500))

    outcome = perform_http_check(monitor)

    assert outcome.success is False
    assert outcome.status_code == 500
    assert "500" in outcome.error_message


@respx.mock
def test_perform_http_check_connection_error(db_session: Session):
    monitor = make_monitor(db_session)
    respx.get(monitor.url).mock(side_effect=httpx.ConnectError("recusado"))

    outcome = perform_http_check(monitor)

    assert outcome.success is False
    assert outcome.status_code is None
    assert outcome.error_message == "recusado"


@respx.mock
def test_record_check_opens_incident_on_failure(db_session: Session):
    monitor = make_monitor(db_session, status=MonitorStatus.UP)
    respx.get(monitor.url).mock(return_value=httpx.Response(500))

    outcome = perform_http_check(monitor)
    record_check(db_session, monitor, outcome)

    assert monitor.status == MonitorStatus.DOWN
    incidents = db_session.query(Incident).filter_by(monitor_id=monitor.id).all()
    assert len(incidents) == 1
    assert incidents[0].resolved_at is None


@respx.mock
def test_record_check_resolves_incident_on_recovery(db_session: Session):
    monitor = make_monitor(db_session, status=MonitorStatus.DOWN)
    incident = Incident(monitor_id=monitor.id, cause="fora do ar")
    db_session.add(incident)
    db_session.commit()

    respx.get(monitor.url).mock(return_value=httpx.Response(200))
    outcome = perform_http_check(monitor)
    record_check(db_session, monitor, outcome)

    assert monitor.status == MonitorStatus.UP
    db_session.refresh(incident)
    assert incident.resolved_at is not None


@respx.mock
def test_record_check_keeps_incident_open_while_still_down(db_session: Session):
    monitor = make_monitor(db_session, status=MonitorStatus.DOWN)
    incident = Incident(monitor_id=monitor.id, cause="fora do ar")
    db_session.add(incident)
    db_session.commit()

    respx.get(monitor.url).mock(return_value=httpx.Response(500))
    outcome = perform_http_check(monitor)
    record_check(db_session, monitor, outcome)

    open_incidents = db_session.query(Incident).filter_by(monitor_id=monitor.id, resolved_at=None).all()
    assert len(open_incidents) == 1
