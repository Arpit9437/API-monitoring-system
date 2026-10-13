import { useCallback, useState } from "react";

import { createMonitor, deleteMonitor, updateMonitor } from "../api/client";
import { Modal } from "../components/Modal";
import { MonitorCard } from "../components/MonitorCard";
import { MonitorForm } from "../components/MonitorForm";
import { useMonitorEvents } from "../hooks/useMonitorEvents";
import { useMonitors } from "../hooks/useMonitors";

export function Dashboard() {
  const { monitors, isLoading, error, refresh, applyMonitor, patchMonitor, removeMonitor } = useMonitors();
  const [modalState, setModalState] = useState(null);

  useMonitorEvents(
    useCallback(
      (event) => {
        patchMonitor(event.monitor_id, {
          status: event.status,
          last_checked_at: event.check.checked_at,
        });
      },
      [patchMonitor]
    )
  );

  async function handleCreate(values) {
    const monitor = await createMonitor(values);
    applyMonitor(monitor);
    setModalState(null);
  }

  async function handleEdit(values) {
    if (modalState?.mode !== "edit") return;
    const monitor = await updateMonitor(modalState.monitor.id, values);
    applyMonitor(monitor);
    setModalState(null);
  }

  async function handleDelete(monitor) {
    const confirmed = window.confirm(`Remove the monitor "${monitor.name}"?`);
    if (!confirmed) return;
    await deleteMonitor(monitor.id);
    removeMonitor(monitor.id);
  }

  return (
    <div className="page">
      <header className="page__header">
        <div>
          <h1>Monitors</h1>
          <p className="page__subtitle">Real-time availability monitoring for your services.</p>
        </div>
        <button className="button" onClick={() => setModalState({ mode: "create" })}>
          New monitor
        </button>
      </header>

      {error && (
        <div className="alert alert--error">
          {error}
          <button className="button button--ghost" onClick={refresh}>
            Try again
          </button>
        </div>
      )}

      {isLoading ? (
        <p className="empty-state">Loading monitors...</p>
      ) : monitors.length === 0 ? (
        <p className="empty-state">No monitors yet. Create your first monitor to get started.</p>
      ) : (
        <div className="monitor-grid">
          {monitors.map((monitor) => (
            <MonitorCard
              key={monitor.id}
              monitor={monitor}
              onEdit={(target) => setModalState({ mode: "edit", monitor: target })}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {modalState && (
        <Modal
          title={modalState.mode === "create" ? "New monitor" : "Edit monitor"}
          onClose={() => setModalState(null)}
        >
          <MonitorForm
            key={modalState.mode === "edit" ? modalState.monitor.id : "create"}
            initialValues={modalState.mode === "edit" ? toFormValues(modalState.monitor) : undefined}
            submitLabel={modalState.mode === "create" ? "Create monitor" : "Save changes"}
            onSubmit={modalState.mode === "create" ? handleCreate : handleEdit}
            onCancel={() => setModalState(null)}
          />
        </Modal>
      )}
    </div>
  );
}

function toFormValues(monitor) {
  return {
    name: monitor.name,
    url: monitor.url,
    method: monitor.method,
    expected_status: monitor.expected_status,
    interval_seconds: monitor.interval_seconds,
    timeout_seconds: monitor.timeout_seconds,
    is_active: monitor.is_active,
  };
}
