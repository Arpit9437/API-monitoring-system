import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getMonitor, getMonitorStats, listChecks, listIncidents } from "../api/client";
import { CheckHistoryTable } from "../components/CheckHistoryTable";
import { IncidentList } from "../components/IncidentList";
import { ResponseTimeChart } from "../components/ResponseTimeChart";
import { StatusBadge } from "../components/StatusBadge";
import { useMonitorEvents } from "../hooks/useMonitorEvents";

export function MonitorDetail() {
  const params = useParams();
  const monitorId = Number(params.id);

  const [monitor, setMonitor] = useState(null);
  const [checks, setChecks] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  const latestRequestId = useRef(0);

  const loadData = useCallback(async () => {
    const requestId = ++latestRequestId.current;
    try {
      const [monitorData, checksData, incidentsData, statsData] = await Promise.all([
        getMonitor(monitorId),
        listChecks(monitorId, 100),
        listIncidents(monitorId),
        getMonitorStats(monitorId),
      ]);
      if (requestId !== latestRequestId.current) return;
      setMonitor(monitorData);
      setChecks(checksData);
      setIncidents(incidentsData);
      setStats(statsData);
      setError(null);
    } catch (err) {
      if (requestId !== latestRequestId.current) return;
      setError(err instanceof Error ? err.message : "Failed to load monitor.");
    }
  }, [monitorId]);

  useEffect(() => {
    setMonitor(null);
    setChecks([]);
    setIncidents([]);
    setStats(null);
    setError(null);
    loadData();
  }, [loadData]);

  useMonitorEvents(
    useCallback(
      (event) => {
        if (event.monitor_id !== monitorId) return;
        loadData();
      },
      [monitorId, loadData]
    )
  );

  if (error) {
    return (
      <div className="page">
        <Link className="button button--ghost" to="/">
          Back
        </Link>
        <p className="alert alert--error">{error}</p>
      </div>
    );
  }

  if (!monitor) {
    return (
      <div className="page">
        <p className="empty-state">Loading monitor...</p>
      </div>
    );
  }

  return (
    <div className="page">
      <Link className="button button--ghost" to="/">
        Back
      </Link>

      <header className="page__header">
        <div>
          <h1>{monitor.name}</h1>
          <p className="page__subtitle">{monitor.url}</p>
        </div>
        <StatusBadge status={monitor.status} />
      </header>

      <div className="monitor-detail__metrics">
        <div className="metric metric--large">
          <span className="metric__label">Uptime (24h)</span>
          <span className="metric__value">{stats ? `${stats.uptime_percentage}%` : "-"}</span>
        </div>
        <div className="metric metric--large">
          <span className="metric__label">Average latency</span>
          <span className="metric__value">
            {stats?.average_response_time_ms != null ? `${Math.round(stats.average_response_time_ms)} ms` : "-"}
          </span>
        </div>
        <div className="metric metric--large">
          <span className="metric__label">Check interval</span>
          <span className="metric__value">{monitor.interval_seconds}s</span>
        </div>
      </div>

      <section className="panel">
        <h2>Response time</h2>
        <ResponseTimeChart checks={checks} />
      </section>

      <section className="panel">
        <h2>Incidents</h2>
        <IncidentList incidents={incidents} />
      </section>

      <section className="panel">
        <h2>Check history</h2>
        <CheckHistoryTable checks={checks} />
      </section>
    </div>
  );
}
