import pandas as pd
import pandas_ta as ta
from analyst.strategies.base import BaseStrategy
from shared.models import StrategyResult, SignalAction


class RSIStrategy(BaseStrategy):
    def calculate(self, df: pd.DataFrame) -> StrategyResult:
        period = self.params.get("period", 14)
        oversold = self.params.get("oversold", 30)
        overbought = self.params.get("overbought", 70)

        rsi = ta.rsi(df["close"], length=period)
        current_rsi = rsi.iloc[-1]

        if current_rsi <= oversold:
            action = SignalAction.BUY
            confidence = max(0.5, (oversold - current_rsi) / oversold)
        elif current_rsi >= overbought:
            action = SignalAction.SELL
            confidence = max(0.5, (current_rsi - overbought) / (100 - overbought))
        else:
            action = SignalAction.HOLD
            confidence = 0.0

        return StrategyResult(
            strategy_name=self.name,
            action=action,
            confidence=min(confidence, 1.0),
            metadata={"rsi": float(current_rsi)},
        )
