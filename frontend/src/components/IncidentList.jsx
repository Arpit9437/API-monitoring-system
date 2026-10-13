function formatDuration(startedAt, resolvedAt) {
  const start = new Date(startedAt).getTime();
  const end = resolvedAt ? new Date(resolvedAt).getTime() : Date.now();
  const minutes = Math.max(1, Math.round((end - start) / 60000));

  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes} min`;
}

export function IncidentList({ incidents }) {
  if (incidents.length === 0) {
    return <p className="empty-state">No incidents recorded.</p>;
  }

  return (
    <ul className="incident-list">
      {incidents.map((incident) => (
        <li key={incident.id} className="incident-list__item">
          <span className={`incident-dot ${incident.is_active ? "incident-dot--active" : ""}`} />
          <div className="incident-list__content">
            <p className="incident-list__cause">{incident.cause}</p>
            <p className="incident-list__meta">
              {new Date(incident.started_at).toLocaleString("en-US")} · duration{" "}
              {formatDuration(incident.started_at, incident.resolved_at)}
              {incident.is_active && " · ongoing"}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}
