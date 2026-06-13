const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  status: () => request<import("../types").BotStatus>("/api/status"),
  signals: () => request<import("../types").Signal[]>("/api/signals"),
  positions: () => request<import("../types").Position[]>("/api/positions"),
  trades: () => request<import("../types").Trade[]>("/api/trades"),
  performance: () => request<import("../types").PerformanceData>("/api/performance"),
  override: (action: string, symbol: string) =>
    request<{ success: boolean }>("/api/override", {
      method: "POST",
      body: JSON.stringify({ action, symbol }),
    }),
  settings: () => request<Record<string, unknown>>("/api/settings"),
  updateSettings: (settings: Record<string, unknown>) =>
    request<{ success: boolean }>("/api/settings", {
      method: "PUT",
      body: JSON.stringify(settings),
    }),
};
