import { useCallback, useEffect, useState } from "react";

import { listMonitors } from "../api/client";

export function useMonitors() {
  const [monitors, setMonitors] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listMonitors();
      setMonitors(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load monitors.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const applyMonitor = useCallback((monitor) => {
    setMonitors((current) => {
      const exists = current.some((item) => item.id === monitor.id);
      if (exists) {
        return current.map((item) => (item.id === monitor.id ? monitor : item));
      }
      return [...current, monitor];
    });
  }, []);

  const patchMonitor = useCallback((id, patch) => {
    setMonitors((current) => current.map((item) => (item.id === id ? { ...item, ...patch } : item)));
  }, []);

  const removeMonitor = useCallback((id) => {
    setMonitors((current) => current.filter((item) => item.id !== id));
  }, []);

  return { monitors, isLoading, error, refresh, applyMonitor, patchMonitor, removeMonitor };
}
