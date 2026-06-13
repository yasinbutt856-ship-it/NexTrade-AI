from abc import ABC, abstractmethod
import pandas as pd
from shared.models import StrategyResult


class BaseStrategy(ABC):
    def __init__(self, name: str, weight: float, params: dict):
        self.name = name
        self.weight = weight
        self.params = params

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> StrategyResult:
        ...
