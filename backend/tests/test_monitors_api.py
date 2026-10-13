from fastapi.testclient import TestClient


def create_sample_monitor(client: TestClient, **overrides) -> dict:
    payload = {
        "name": "API principal",
        "url": "https://example.com/health",
        "method": "GET",
        "expected_status": 200,
        "interval_seconds": 60,
        "timeout_seconds": 5,
    }
    payload.update(overrides)
    response = client.post("/api/monitors", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_monitor(client: TestClient):
    monitor = create_sample_monitor(client)

    assert monitor["name"] == "API principal"
    assert monitor["status"] == "unknown"
    assert monitor["is_active"] is True
    assert monitor["last_checked_at"] is None


def test_create_monitor_rejects_invalid_url(client: TestClient):
    response = client.post("/api/monitors", json={"name": "invalido", "url": "nao-e-uma-url"})
    assert response.status_code == 422


def test_list_monitors_returns_created_items(client: TestClient):
    create_sample_monitor(client, name="Monitor A")
    create_sample_monitor(client, name="Monitor B", url="https://example.com/b")

    response = client.get("/api/monitors")

    assert response.status_code == 200
    names = {monitor["name"] for monitor in response.json()}
    assert names == {"Monitor A", "Monitor B"}


def test_get_monitor_not_found(client: TestClient):
    response = client.get("/api/monitors/999")
    assert response.status_code == 404


def test_update_monitor(client: TestClient):
    monitor = create_sample_monitor(client)

    response = client.patch(f"/api/monitors/{monitor['id']}", json={"interval_seconds": 120, "is_active": False})

    assert response.status_code == 200
    updated = response.json()
    assert updated["interval_seconds"] == 120
    assert updated["is_active"] is False
    assert updated["name"] == monitor["name"]


def test_update_monitor_ignores_explicit_null_url(client: TestClient):
    monitor = create_sample_monitor(client)

    response = client.patch(f"/api/monitors/{monitor['id']}", json={"url": None})

    assert response.status_code == 200
    assert response.json()["url"] == monitor["url"]


def test_delete_monitor(client: TestClient):
    monitor = create_sample_monitor(client)

    delete_response = client.delete(f"/api/monitors/{monitor['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/monitors/{monitor['id']}")
    assert get_response.status_code == 404


def test_monitor_stats_with_no_checks(client: TestClient):
    monitor = create_sample_monitor(client)

    response = client.get(f"/api/monitors/{monitor['id']}/stats")

    assert response.status_code == 200
    stats = response.json()
    assert stats["total_checks"] == 0
    assert stats["uptime_percentage"] == 100.0
    assert stats["average_response_time_ms"] is None


def test_monitor_stats_rejects_out_of_range_window_hours(client: TestClient):
    monitor = create_sample_monitor(client)

    response = client.get(f"/api/monitors/{monitor['id']}/stats?window_hours=999999999999")

    assert response.status_code == 422
