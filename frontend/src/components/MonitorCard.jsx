import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getMonitorStats } from "../api/client";
import { StatusBadge } from "./StatusBadge";

export function MonitorCard({ monitor, onEdit, onDelete }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getMonitorStats(monitor.id)
      .then((data) => {
        if (!cancelled) setStats(data);
      })
      .catch(() => {
        if (!cancelled) setStats(null);
      });
    return () => {
      cancelled = true;
    };
  }, [monitor.id, monitor.last_checked_at]);

  return (
    <article className="monitor-card">
      <header className="monitor-card__header">
        <div>
          <h3>{monitor.name}</h3>
          <p className="monitor-card__url">{monitor.url}</p>
        </div>
        <StatusBadge status={monitor.status} />
      </header>

      <div className="monitor-card__metrics">
        <div className="metric">
          <span className="metric__label">Uptime (24h)</span>
          <span className="metric__value">{stats ? `${stats.uptime_percentage}%` : "-"}</span>
        </div>
        <div className="metric">
          <span className="metric__label">Average latency</span>
          <span className="metric__value">
            {stats?.average_response_time_ms != null ? `${Math.round(stats.average_response_time_ms)} ms` : "-"}
          </span>
        </div>
        <div className="metric">
          <span className="metric__label">Checks (24h)</span>
          <span className="metric__value">{stats?.total_checks ?? "-"}</span>
        </div>
      </div>

      <footer className="monitor-card__footer">
        <Link className="button button--ghost" to={`/monitors/${monitor.id}`}>
          View details
        </Link>
        <button className="button button--ghost" onClick={() => onEdit(monitor)}>
          Edit
        </button>
        <button className="button button--danger" onClick={() => onDelete(monitor)}>
          Remove
        </button>
      </footer>
    </article>
  );
}
