export type SignalAction = "buy" | "sell" | "hold";
export type BotMode = "paper" | "live";
export type TradeType = "spot" | "futures";
export type OrderStatus = "pending" | "open" | "filled" | "canceled" | "rejected" | "expired";
export type PlanType = "basic" | "pro" | "enterprise";

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
  timeframe?: string;
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

export interface SiteStats {
  total_users: number;
  weekly_users: number;
  total_trades: number;
  win_rate: number;
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

export interface AuthResponse {
  token: string;
  email: string;
  is_admin: boolean;
  plan: PlanType;
  mode: BotMode;
  trade_type: TradeType;
  bot_active: boolean;
  wallet_address?: string;
  wallet_type?: string;
}

export interface WalletInfo {
  wallet_address: string;
  wallet_type: string;
  has_wallet: boolean;
}

export interface UserProfile {
  id: number;
  email: string;
  is_admin: boolean;
  plan: PlanType;
  mode: BotMode;
  trade_type: TradeType;
  bot_active: boolean;
  max_position_usdt: number;
  has_mexc_keys: boolean;
  wallet_address?: string;
  wallet_type?: string;
  withdrawal_delay_hours?: number;
}

export interface UserSettings {
  mode: BotMode;
  trade_type: TradeType;
  max_position_usdt: number;
}

export interface MexcKeys {
  api_key: string;
  api_secret: string;
  has_keys: boolean;
}

export interface BotControlStatus {
  bot_active: boolean;
  mode: BotMode;
  trade_type: TradeType;
  has_mexc_keys: boolean;
  plan: PlanType;
  max_position_usdt: number;
}

export interface BotLogEntry {
  level: string;
  message: string;
  timestamp: string;
  [key: string]: unknown;
}

export interface WhitelistEntry {
  id: number;
  address: string;
  network: string;
  label: string;
  is_approved: boolean;
  created_at: string;
}

export interface AdminPendingApproval extends WhitelistEntry {
  user_email: string;
  user_id: number;
}

export interface PortfolioStats {
  total_pnl: number;
  total_trades: number;
  win_rate: number;
  open_positions: number;
  total_unrealized_pnl: number;
  total_invested: number;
  pair_breakdown: { symbol: string; trades: number; pnl: number }[];
}

export interface NotificationPrefs {
  email: boolean;
  telegram: boolean;
  push: boolean;
}

export interface UserApiKey {
  id: number;
  key_prefix: string;
  name: string | null;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
}

export interface AdminAnalytics {
  total_users: number;
  monthly_users: number;
  active_bots: number;
  total_trades: number;
  total_pnl: number;
  plan_breakdown: { basic: number; pro: number; enterprise: number };
  user_growth: { month: string; new_users: number }[];
}

export interface AdminUser {
  id: number;
  email: string;
  plan: PlanType;
  mode: BotMode;
  trade_type: TradeType;
  bot_active: boolean;
  is_admin: boolean;
  has_mexc_keys: boolean;
  max_position_usdt: number;
  created_at: string | null;
  wallet_address?: string;
  wallet_type?: string;
}
