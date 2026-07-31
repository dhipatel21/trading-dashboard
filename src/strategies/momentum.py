"""Momentum / benchmark strategies."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Strategy, register


def time_series_momentum(df: pd.DataFrame, lookback: int = 126) -> pd.Series:
    """Long if trailing `lookback`-day return is positive, flat/short otherwise.

    This is the single-asset version of Moskowitz/Ooi/Pedersen's
    'Time Series Momentum' — one of the most cited systematic strategies
    in the academic literature, still core to many CTA/managed-futures funds.
    """
    ret = df["Close"].pct_change(lookback)
    return pd.Series(np.where(ret > 0, 1, -1), index=df.index)


def dual_momentum(df: pd.DataFrame, lookback: int = 126, vol_window: int = 20) -> pd.Series:
    """Time-series momentum gated by a volatility filter (skip when vol is in the top quartile)."""
    ret = df["Close"].pct_change(lookback)
    daily_ret = df["Close"].pct_change()
    vol = daily_ret.rolling(vol_window).std()
    vol_thresh = vol.rolling(252, min_periods=vol_window).quantile(0.75)
    calm = vol <= vol_thresh
    sig = pd.Series(np.where(ret > 0, 1, 0), index=df.index)
    sig = sig.where(calm.fillna(True), 0)
    return sig


def buy_and_hold(df: pd.DataFrame) -> pd.Series:
    """Always long. The benchmark every other strategy has to beat."""
    return pd.Series(1, index=df.index)


register(Strategy(
    key="time_series_momentum",
    name="Time-Series Momentum (12-1)",
    category="Momentum",
    description="Long when trailing ~6-month return is positive, short when negative. "
                "One of the most replicated systematic strategies in finance.",
    reference="Moskowitz, Ooi & Pedersen, 'Time Series Momentum', Journal of Financial "
              "Economics (2012).",
    signal_fn=time_series_momentum,
    params={"lookback": 126},
))

register(Strategy(
    key="dual_momentum",
    name="Volatility-Managed Momentum",
    category="Momentum",
    description="Time-series momentum that stands aside when realized volatility is in "
                "its own top quartile — momentum crashes are concentrated in high-vol regimes.",
    reference="Barroso & Santa-Clara, 'Momentum Has Its Moments', Journal of Financial "
              "Economics (2015); Moreira & Muir, 'Volatility-Managed Portfolios' (2017).",
    signal_fn=dual_momentum,
    params={"lookback": 126, "vol_window": 20},
))

register(Strategy(
    key="buy_and_hold",
    name="Buy & Hold (Benchmark)",
    category="Benchmark",
    description="Always fully long, no trading. The baseline every active strategy is "
                "measured against.",
    reference="—",
    signal_fn=buy_and_hold,
    params={},
))
