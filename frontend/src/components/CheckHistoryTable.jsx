export function CheckHistoryTable({ checks }) {
  if (checks.length === 0) {
    return <p className="empty-state">No checks recorded yet.</p>;
  }

  return (
    <table className="check-table">
      <thead>
        <tr>
          <th>Time</th>
          <th>Result</th>
          <th>HTTP status</th>
          <th>Response time</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
        {checks.map((check) => (
          <tr key={check.id}>
            <td>{new Date(check.checked_at).toLocaleString("en-US")}</td>
            <td>
              <span className={`check-result check-result--${check.success ? "success" : "failure"}`}>
                {check.success ? "Success" : "Failure"}
              </span>
            </td>
            <td>{check.status_code ?? "-"}</td>
            <td>{check.response_time_ms != null ? `${Math.round(check.response_time_ms)} ms` : "-"}</td>
            <td>{check.error_message ?? "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
