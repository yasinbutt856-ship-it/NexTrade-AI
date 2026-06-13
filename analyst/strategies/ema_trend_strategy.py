import pandas as pd
import pandas_ta as ta
from analyst.strategies.base import BaseStrategy
from shared.models import StrategyResult, SignalAction


class EMATrendStrategy(BaseStrategy):
    def calculate(self, df: pd.DataFrame) -> StrategyResult:
        short_period = self.params.get("short_period", 9)
        long_period = self.params.get("long_period", 21)

        ema_short = ta.ema(df["close"], length=short_period)
        ema_long = ta.ema(df["close"], length=long_period)

        prev_short = ema_short.iloc[-2]
        prev_long = ema_long.iloc[-2]
        curr_short = ema_short.iloc[-1]
        curr_long = ema_long.iloc[-1]

        if prev_short <= prev_long and curr_short > curr_long:
            action = SignalAction.BUY
            confidence = 0.65
        elif prev_short >= prev_long and curr_short < curr_long:
            action = SignalAction.SELL
            confidence = 0.65
        else:
            action = SignalAction.HOLD
            confidence = 0.0

        return StrategyResult(
            strategy_name=self.name,
            action=action,
            confidence=confidence,
            metadata={
                "ema_short": float(curr_short),
                "ema_long": float(curr_long),
            },
        )
