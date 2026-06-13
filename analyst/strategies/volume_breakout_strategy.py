import pandas as pd
import pandas_ta as ta
from analyst.strategies.base import BaseStrategy
from shared.models import StrategyResult, SignalAction


class VolumeBreakoutStrategy(BaseStrategy):
    def calculate(self, df: pd.DataFrame) -> StrategyResult:
        period = self.params.get("volume_ma_period", 20)
        multiplier = self.params.get("breakout_multiplier", 2.0)

        volume_ma = ta.sma(df["volume"], length=period)
        current_volume = df["volume"].iloc[-1]
        avg_volume = volume_ma.iloc[-1]

        if avg_volume == 0:
            return StrategyResult(
                strategy_name=self.name,
                action=SignalAction.HOLD,
                confidence=0.0,
                metadata={"volume_ratio": 0.0},
            )

        volume_ratio = current_volume / avg_volume

        if volume_ratio >= multiplier:
            price_change = (
                (df["close"].iloc[-1] - df["close"].iloc[-2])
                / df["close"].iloc[-2]
            )
            if price_change > 0:
                action = SignalAction.BUY
            else:
                action = SignalAction.SELL
            confidence = min(0.5 + (volume_ratio - multiplier) * 0.2, 0.9)
        else:
            action = SignalAction.HOLD
            confidence = 0.0

        return StrategyResult(
            strategy_name=self.name,
            action=action,
            confidence=confidence,
            metadata={"volume_ratio": float(volume_ratio)},
        )
