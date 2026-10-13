import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function ResponseTimeChart({ checks }) {
  const data = [...checks]
    .reverse()
    .map((check) => ({
      time: new Date(check.checked_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
      responseTime: check.response_time_ms != null ? Math.round(check.response_time_ms) : null,
    }));

  if (data.length === 0) {
    return <p className="empty-state">No checks recorded yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
        <XAxis dataKey="time" stroke="var(--color-text-muted)" fontSize={12} />
        <YAxis stroke="var(--color-text-muted)" fontSize={12} unit="ms" width={60} />
        <Tooltip
          contentStyle={{ background: "var(--color-surface)", border: "1px solid var(--color-border)" }}
          labelStyle={{ color: "var(--color-text)" }}
        />
        <Line
          type="monotone"
          dataKey="responseTime"
          name="Response time"
          stroke="var(--color-accent)"
          strokeWidth={2}
          dot={false}
          connectNulls
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
