"""
Strategy base class + registry.

Every strategy implements `generate_signals(df) -> pd.Series` of {-1, 0, 1}
(short/flat/long) indexed like `df`. The backtester shifts this by one bar
before applying returns, so signals are never allowed to see the future.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd


@dataclass
class Strategy:
    key: str
    name: str
    category: str
    description: str
    reference: str
    signal_fn: Callable[[pd.DataFrame], pd.Series]
    params: dict = field(default_factory=dict)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        sig = self.signal_fn(df, **self.params) if self.params else self.signal_fn(df)
        sig = sig.reindex(df.index).fillna(0)
        return sig.clip(-1, 1)


REGISTRY: dict[str, Strategy] = {}


def register(strategy: Strategy) -> Strategy:
    REGISTRY[strategy.key] = strategy
    return strategy


def all_strategies() -> list[Strategy]:
    return list(REGISTRY.values())


def get(key: str) -> Strategy:
    return REGISTRY[key]
