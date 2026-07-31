"""Mean-reversion / statistical strategies."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Strategy, register


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def rsi_mean_reversion(df: pd.DataFrame, period: int = 14, low: int = 30, high: int = 70) -> pd.Series:
    """Long when RSI dips under `low` (oversold), flat once it recovers above `high`."""
    rsi = _rsi(df["Close"], period)
    sig = pd.Series(np.nan, index=df.index)
    sig[rsi < low] = 1
    sig[rsi > high] = 0
    return sig.ffill().fillna(0)


def bollinger_reversion(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.Series:
    """Long below the lower Bollinger Band, flat once price reverts to the middle band (SMA)."""
    mid = df["Close"].rolling(window).mean()
    std = df["Close"].rolling(window).std()
    lower = mid - num_std * std
    close = df["Close"]
    sig = pd.Series(np.nan, index=df.index)
    sig[close < lower] = 1
    sig[close > mid] = 0
    return sig.ffill().fillna(0)


def zscore_mean_reversion(df: pd.DataFrame, window: int = 20, entry_z: float = 1.5, exit_z: float = 0.25) -> pd.Series:
    """Trade the z-score of price vs its rolling mean — long when far below, exit near the mean."""
    mean = df["Close"].rolling(window).mean()
    std = df["Close"].rolling(window).std()
    z = (df["Close"] - mean) / std.replace(0, np.nan)
    sig = pd.Series(np.nan, index=df.index)
    sig[z < -entry_z] = 1
    sig[z > -exit_z] = 0
    return sig.ffill().fillna(0)


register(Strategy(
    key="rsi_mean_reversion",
    name="RSI Oversold/Overbought",
    category="Mean Reversion",
    description="Buys when the 14-day RSI falls below 30 (oversold) and exits once it "
                "climbs back above 70. Classic contrarian/mean-reversion signal.",
    reference="J. Welles Wilder, 'New Concepts in Technical Trading Systems' (1978).",
    signal_fn=rsi_mean_reversion,
    params={"period": 14, "low": 30, "high": 70},
))

register(Strategy(
    key="bollinger_reversion",
    name="Bollinger Band Reversion",
    category="Mean Reversion",
    description="Buys when price closes below the lower Bollinger Band (2 std devs under "
                "the 20-day mean) and exits once price reverts to the moving average.",
    reference="John Bollinger, Bollinger Bands (1980s).",
    signal_fn=bollinger_reversion,
    params={"window": 20, "num_std": 2.0},
))

register(Strategy(
    key="zscore_mean_reversion",
    name="Rolling Z-Score Reversion",
    category="Mean Reversion / Statistical",
    description="Standardizes price against its own rolling distribution and trades the "
                "z-score extremes — a lightweight version of the statistical-arbitrage "
                "'distance method' used in pairs trading, applied to a single asset.",
    reference="Gatev, Goetzmann & Rouwenhorst, 'Pairs Trading: Performance of a "
              "Relative-Value Arbitrage Rule' (2006).",
    signal_fn=zscore_mean_reversion,
    params={"window": 20, "entry_z": 1.5, "exit_z": 0.25},
))
