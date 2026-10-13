const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request(path, init) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail ?? response.statusText;
    throw new Error(typeof detail === "string" ? detail : "Unexpected API error.");
  }

  if (response.status === 204) {
    return undefined;
  }

  return response.json();
}

export function listMonitors() {
  return request("/api/monitors");
}

export function getMonitor(id) {
  return request(`/api/monitors/${id}`);
}

export function createMonitor(values) {
  return request("/api/monitors", {
    method: "POST",
    body: JSON.stringify(values),
  });
}

export function updateMonitor(id, values) {
  return request(`/api/monitors/${id}`, {
    method: "PATCH",
    body: JSON.stringify(values),
  });
}

export function deleteMonitor(id) {
  return request(`/api/monitors/${id}`, { method: "DELETE" });
}

export function getMonitorStats(id, windowHours = 24) {
  return request(`/api/monitors/${id}/stats?window_hours=${windowHours}`);
}

export function listChecks(monitorId, limit = 50) {
  return request(`/api/monitors/${monitorId}/checks?limit=${limit}`);
}

export function listIncidents(monitorId, activeOnly = false) {
  const params = new URLSearchParams();
  if (monitorId !== undefined) params.set("monitor_id", String(monitorId));
  if (activeOnly) params.set("active_only", "true");
  const query = params.toString();
  return request(`/api/incidents${query ? `?${query}` : ""}`);
}
