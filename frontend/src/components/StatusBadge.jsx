const LABELS = {
  up: "Operational",
  down: "Down",
  unknown: "Awaiting first check",
};

export function StatusBadge({ status }) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      <span className="status-badge__dot" />
      {LABELS[status]}
    </span>
  );
}
