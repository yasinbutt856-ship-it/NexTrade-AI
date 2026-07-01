import { useEffect, useRef, useCallback } from "react";
import { getToken } from "../api/client";

const BASE_URL = import.meta.env.VITE_API_URL || "https://5148f32ad99cf7d9-154-81-236-235.serveousercontent.com";

const WS_BASE = BASE_URL.replace(/^http/, "ws");

export type WSMessage = {
  type: "status" | "signals" | "positions" | "performance" | "logs";
  data: unknown;
};

export function useWebSocket(onMessage: (msg: WSMessage) => void) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const wsRef = useRef<WebSocket>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const attemptRef = useRef(0);

  const connect = useCallback(() => {
    const token = getToken();
    if (!token) return;

    const ws = new WebSocket(`${WS_BASE}/ws?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      attemptRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data) as WSMessage;
        onMessageRef.current(msg);
      } catch {
        /* ignore malformed messages */
      }
    };

    ws.onclose = (event) => {
      if (event.code === 4001) {
        localStorage.removeItem("token");
        window.location.href = "/login";
        return;
      }
      const delay = Math.min(1000 * Math.pow(2, attemptRef.current), 30000);
      attemptRef.current += 1;
      reconnectTimerRef.current = setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      clearTimeout(reconnectTimerRef.current);
    };
  }, [connect]);
}
