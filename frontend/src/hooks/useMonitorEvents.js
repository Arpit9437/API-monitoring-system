import { useEffect, useRef } from "react";

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000";
const RECONNECT_DELAY_MS = 3000;

export function useMonitorEvents(onEvent) {
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    let socket = null;
    let reconnectTimer = null;
    let closedByCleanup = false;

    function connect() {
      socket = new WebSocket(`${WS_URL}/ws/monitors`);

      socket.onmessage = (message) => {
        try {
          const event = JSON.parse(message.data);
          onEventRef.current(event);
        } catch {
          return;
        }
      };

      socket.onclose = () => {
        if (!closedByCleanup) {
          reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
        }
      };
    }

    connect();

    return () => {
      closedByCleanup = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);
}
