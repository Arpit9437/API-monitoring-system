import { useState } from "react";

const DEFAULT_VALUES = {
  name: "",
  url: "",
  method: "GET",
  expected_status: 200,
  interval_seconds: 60,
  timeout_seconds: 5,
  is_active: true,
};

export function MonitorForm({ initialValues, submitLabel, onSubmit, onCancel }) {
  const [values, setValues] = useState(initialValues ?? DEFAULT_VALUES);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit(values);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save monitor.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="monitor-form" onSubmit={handleSubmit}>
      <label className="monitor-form__field">
        <span>Name</span>
        <input
          required
          value={values.name}
          onChange={(event) => setValues({ ...values, name: event.target.value })}
        />
      </label>

      <label className="monitor-form__field">
        <span>URL</span>
        <input
          required
          type="url"
          placeholder="https://example.com/health"
          value={values.url}
          onChange={(event) => setValues({ ...values, url: event.target.value })}
        />
      </label>

      <div className="monitor-form__row">
        <label className="monitor-form__field">
          <span>Method</span>
          <select
            value={values.method}
            onChange={(event) => setValues({ ...values, method: event.target.value })}
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="HEAD">HEAD</option>
          </select>
        </label>

        <label className="monitor-form__field">
          <span>Expected status</span>
          <input
            type="number"
            min={100}
            max={599}
            value={values.expected_status}
            onChange={(event) => setValues({ ...values, expected_status: Number(event.target.value) })}
          />
        </label>
      </div>

      <div className="monitor-form__row">
        <label className="monitor-form__field">
          <span>Interval (seconds)</span>
          <input
            type="number"
            min={5}
            max={86400}
            value={values.interval_seconds}
            onChange={(event) => setValues({ ...values, interval_seconds: Number(event.target.value) })}
          />
        </label>

        <label className="monitor-form__field">
          <span>Timeout (seconds)</span>
          <input
            type="number"
            min={1}
            max={60}
            value={values.timeout_seconds}
            onChange={(event) => setValues({ ...values, timeout_seconds: Number(event.target.value) })}
          />
        </label>
      </div>

      <label className="monitor-form__checkbox">
        <input
          type="checkbox"
          checked={values.is_active}
          onChange={(event) => setValues({ ...values, is_active: event.target.checked })}
        />
        <span>Monitor is active</span>
      </label>

      {error && <p className="monitor-form__error">{error}</p>}

      <div className="monitor-form__actions">
        <button type="button" className="button button--ghost" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </button>
        <button type="submit" className="button" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
