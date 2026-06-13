export type SignalAction = "buy" | "sell" | "hold";
export type BotMode = "paper" | "live";
export type OrderStatus = "pending" | "open" | "filled" | "canceled" | "rejected" | "expired";

export interface StrategyResult {
  strategy_name: string;
  action: SignalAction;
  confidence: number;
  metadata: Record<string, unknown>;
}

export interface Signal {
  symbol: string;
  action: SignalAction;
  confidence: number;
  price: number;
  timestamp: string;
  strategy_results: StrategyResult[];
}

export interface Position {
  id: string;
  symbol: string;
  side: "buy" | "sell";
  entry_price: number;
  current_price: number;
  quantity: number;
  unrealized_pnl: number;
  realized_pnl: number;
  stop_loss: number | null;
  take_profit: number | null;
  opened_at: string;
  closed_at: string | null;
  status: OrderStatus;
}

export interface Trade {
  id: string;
  symbol: string;
  side: "buy" | "sell";
  price: number;
  quantity: number;
  total: number;
  fee: number;
  timestamp: string;
}

export interface BotStatus {
  mode: BotMode;
  analyst_alive: boolean;
  trader_alive: boolean;
  uptime_seconds: number;
}

export interface PerformanceData {
  total_pnl: number;
  win_rate: number;
  total_trades: number;
  equity_curve: { date: string; value: number }[];
}
