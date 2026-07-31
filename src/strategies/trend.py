"""Classic trend-following strategies: moving-average crossovers and channel breakouts."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Strategy, register


def sma_crossover(df: pd.DataFrame, fast: int = 50, slow: int = 200) -> pd.Series:
    """Golden/death cross. Long while fast SMA > slow SMA, else flat."""
    fast_ma = df["Close"].rolling(fast).mean()
    slow_ma = df["Close"].rolling(slow).mean()
    return pd.Series(np.where(fast_ma > slow_ma, 1, 0), index=df.index)


def ema_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    """MACD line vs signal line crossover — faster trend/momentum blend."""
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return pd.Series(np.where(macd > signal_line, 1, -1), index=df.index)


def donchian_breakout(df: pd.DataFrame, entry: int = 20, exit_: int = 10) -> pd.Series:
    """Turtle-style channel breakout: long on N-day high breakout, flat on M-day low breakdown."""
    upper = df["High"].rolling(entry).max()
    lower = df["Low"].rolling(exit_).min()
    close = df["Close"]

    sig = pd.Series(0, index=df.index, dtype=float)
    position = 0
    upper_shift = upper.shift(1)
    lower_shift = lower.shift(1)
    for i in range(len(df)):
        c = close.iloc[i]
        u = upper_shift.iloc[i]
        l = lower_shift.iloc[i]
        if pd.notna(u) and c >= u:
            position = 1
        elif pd.notna(l) and c <= l:
            position = 0
        sig.iloc[i] = position
    return sig


register(Strategy(
    key="sma_crossover",
    name="SMA Crossover (Golden/Death Cross)",
    category="Trend Following",
    description="Long when the 50-day SMA is above the 200-day SMA, flat otherwise. "
                "One of the oldest and most widely used systematic trend signals.",
    reference="Classic technical analysis; see Investopedia 'Golden Cross' / Faber (2007) "
              "'A Quantitative Approach to Tactical Asset Allocation'.",
    signal_fn=sma_crossover,
    params={"fast": 50, "slow": 200},
))

register(Strategy(
    key="ema_macd",
    name="MACD Trend/Momentum",
    category="Trend Following",
    description="Long when MACD line is above its signal line, short when below. "
                "Captures medium-term momentum shifts faster than simple MAs.",
    reference="Gerald Appel, MACD (1970s); standard in most charting/TA-Lib toolkits.",
    signal_fn=ema_macd,
    params={"fast": 12, "slow": 26, "signal": 9},
))

register(Strategy(
    key="donchian_breakout",
    name="Donchian Channel Breakout (Turtle)",
    category="Trend Following",
    description="Go long on a 20-day high breakout, exit on a 10-day low breakdown. "
                "The core rule of the legendary 1980s 'Turtle Traders' system.",
    reference="Richard Dennis & William Eckhardt, Turtle Trading rules (1983); "
              "Donchian channel breakout systems.",
    signal_fn=donchian_breakout,
    params={"entry": 20, "exit_": 10},
))
