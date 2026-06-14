import pandas as pd
import pandas_ta as ta
from analyst.strategies.base import BaseStrategy
from shared.models import StrategyResult, SignalAction


class BollingerSqueezeStrategy(BaseStrategy):
    def calculate(self, df: pd.DataFrame) -> StrategyResult:
        period = self.params.get("period", 20)
        std_dev = self.params.get("std_dev", 2)
        squeeze_threshold = self.params.get("squeeze_threshold", 0.05)

        bbands = ta.bbands(df["close"], length=period, std=std_dev)
        upper = bbands.iloc[:, 0]
        mid = bbands.iloc[:, 1]
        lower = bbands.iloc[:, 2]
        bandwidth = bbands.iloc[:, 3]

        current_bandwidth = bandwidth.iloc[-1]
        current_price = df["close"].iloc[-1]
        is_squeeze = current_bandwidth < squeeze_threshold

        if is_squeeze:
            direction = current_price - mid.iloc[-1]
            if direction > 0:
                action = SignalAction.BUY
                confidence = 0.6
            else:
                action = SignalAction.SELL
                confidence = 0.6
        else:
            if current_price >= upper.iloc[-1]:
                action = SignalAction.SELL
                confidence = 0.5
            elif current_price <= lower.iloc[-1]:
                action = SignalAction.BUY
                confidence = 0.5
            else:
                action = SignalAction.HOLD
                confidence = 0.0

        return StrategyResult(
            strategy_name=self.name,
            action=action,
            confidence=confidence,
            metadata={
                "bandwidth": float(current_bandwidth),
                "is_squeeze": bool(is_squeeze),
            },
        )
