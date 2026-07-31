"""
Strategy base class + registry.

Every strategy implements `generate_signals(df) -> pd.Series` of {-1, 0, 1}
(short/flat/long) indexed like `df`. The backtester shifts this by one bar
before applying returns, so signals are never allowed to see the future.

Some strategies (the ML/DL ones) also implement `predict_fn(df) -> dict` which
does one extra final fit on ALL available history and returns a genuine
prediction for the *next*, not-yet-realized bar, plus a confidence score. This
is separate from `generate_signals`'s walk-forward series used for backtesting.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

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
    predict_fn: Optional[Callable[[pd.DataFrame], dict]] = None

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        sig = self.signal_fn(df, **self.params) if self.params else self.signal_fn(df)
        sig = sig.reindex(df.index).fillna(0)
        return sig.clip(-1, 1)

    def predict_latest(self, df: pd.DataFrame) -> dict:
        """Signal + confidence for the next bar. Falls back to the last value
        of the walk-forward signal series (no confidence) if the strategy
        doesn't define a dedicated predict_fn.
        """
        if self.predict_fn is not None:
            return self.predict_fn(df, **self.params) if self.params else self.predict_fn(df)
        sig = self.generate_signals(df)
        return {"signal": int(sig.iloc[-1]), "confidence": None}


REGISTRY: dict[str, Strategy] = {}


def register(strategy: Strategy) -> Strategy:
    REGISTRY[strategy.key] = strategy
    return strategy


def all_strategies() -> list[Strategy]:
    return list(REGISTRY.values())


def get(key: str) -> Strategy:
    return REGISTRY[key]
