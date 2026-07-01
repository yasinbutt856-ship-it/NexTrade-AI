interface BadgeProps {
  variant: "buy" | "sell" | "hold" | "live" | "paper" | "active" | "offline" | "success" | "warning" | "error" | "default";
  children: string;
}

const variants: Record<string, string> = {
  buy: "bg-positive/15 text-positive border border-positive/20",
  sell: "bg-negative/15 text-negative border border-negative/20",
  hold: "bg-gray-500/15 text-gray-400 border border-gray-500/20",
  live: "bg-positive/15 text-positive border border-positive/20",
  paper: "bg-accent/15 text-accent border border-accent/20",
  active: "bg-accent/15 text-accent border border-accent/20",
  offline: "bg-gray-500/10 text-gray-600 border border-gray-500/10",
  success: "bg-positive/15 text-positive border border-positive/20",
  warning: "bg-accent/15 text-accent border border-accent/20",
  error: "bg-negative/15 text-negative border border-negative/20",
  default: "bg-dark-600/50 text-gray-400 border border-white/5",
};

export function Badge({ variant, children }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${variants[variant] || variants.default}`}>
      {children}
    </span>
  );
}
