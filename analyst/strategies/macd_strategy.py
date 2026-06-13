import pandas as pd
import pandas_ta as ta
from analyst.strategies.base import BaseStrategy
from shared.models import StrategyResult, SignalAction


class MACDStrategy(BaseStrategy):
    def calculate(self, df: pd.DataFrame) -> StrategyResult:
        fast = self.params.get("fast", 12)
        slow = self.params.get("slow", 26)
        signal = self.params.get("signal", 9)

        macd = ta.macd(df["close"], fast=fast, slow=slow, signal=signal)
        macd_line = macd.iloc[:, 0]
        signal_line = macd.iloc[:, 1]
        histogram = macd.iloc[:, 2]

        prev_macd = macd_line.iloc[-2]
        prev_signal = signal_line.iloc[-2]
        curr_macd = macd_line.iloc[-1]
        curr_signal = signal_line.iloc[-1]

        if prev_macd <= prev_signal and curr_macd > curr_signal:
            action = SignalAction.BUY
            confidence = 0.7
        elif prev_macd >= prev_signal and curr_macd < curr_signal:
            action = SignalAction.SELL
            confidence = 0.7
        else:
            action = SignalAction.HOLD
            confidence = 0.0

        return StrategyResult(
            strategy_name=self.name,
            action=action,
            confidence=confidence,
            metadata={
                "macd": float(curr_macd),
                "signal": float(curr_signal),
                "histogram": float(histogram.iloc[-1]),
            },
        )
