"""Vectorized backtest engine + standard performance metrics.

Convention: a strategy's signal at bar t (using only information available
through the close of bar t) is executed starting at bar t+1's return. This
one-bar shift is applied here, centrally, so no individual strategy has to
worry about look-ahead bias.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS = 252


@dataclass
class BacktestResult:
    ticker: str
    strategy_key: str
    strategy_name: str
    equity_curve: pd.Series
    returns: pd.Series
    positions: pd.Series
    benchmark_equity: pd.Series
    metrics: dict


def run_backtest(
    df: pd.DataFrame,
    signals: pd.Series,
    cost_bps: float = 5.0,
    initial_capital: float = 10_000.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Returns (equity_curve, strategy_returns, executed_positions)."""
    close = df["Close"]
    asset_ret = close.pct_change().fillna(0)

    position = signals.shift(1).fillna(0)  # decided at t, held during t+1
    trade = position.diff().abs().fillna(abs(position.iloc[0]) if len(position) else 0)
    cost = trade * (cost_bps / 10_000.0)

    strat_ret = position * asset_ret - cost
    equity = initial_capital * (1 + strat_ret).cumprod()
    return equity, strat_ret, position


def compute_metrics(strat_ret: pd.Series, position: pd.Series, benchmark_ret: pd.Series) -> dict:
    strat_ret = strat_ret.fillna(0)
    n = len(strat_ret)
    years = max(n / TRADING_DAYS, 1e-9)

    total_return = (1 + strat_ret).prod() - 1
    cagr = (1 + total_return) ** (1 / years) - 1 if total_return > -1 else -1.0
    ann_vol = strat_ret.std() * np.sqrt(TRADING_DAYS)
    sharpe = (strat_ret.mean() * TRADING_DAYS) / ann_vol if ann_vol > 0 else 0.0

    downside = strat_ret[strat_ret < 0]
    downside_vol = downside.std() * np.sqrt(TRADING_DAYS) if len(downside) else 0.0
    sortino = (strat_ret.mean() * TRADING_DAYS) / downside_vol if downside_vol > 0 else 0.0

    equity = (1 + strat_ret).cumprod()
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    max_dd = drawdown.min()
    calmar = cagr / abs(max_dd) if max_dd < 0 else 0.0

    trades = position.diff().abs().fillna(0)
    n_trades = int((trades > 0).sum())
    win_days = (strat_ret > 0).sum()
    total_active_days = (strat_ret != 0).sum()
    win_rate = win_days / total_active_days if total_active_days > 0 else 0.0

    bench_total = (1 + benchmark_ret.fillna(0)).prod() - 1

    return {
        "Total Return": total_return,
        "CAGR": cagr,
        "Ann. Volatility": ann_vol,
        "Sharpe": sharpe,
        "Sortino": sortino,
        "Max Drawdown": max_dd,
        "Calmar": calmar,
        "Win Rate": win_rate,
        "# Trades": n_trades,
        "Benchmark Return": bench_total,
        "Excess vs Benchmark": total_return - bench_total,
    }


def backtest_strategy(
    df: pd.DataFrame,
    strategy,
    ticker: str,
    cost_bps: float = 5.0,
    initial_capital: float = 10_000.0,
) -> BacktestResult:
    signals = strategy.generate_signals(df)
    equity, strat_ret, position = run_backtest(df, signals, cost_bps, initial_capital)

    bench_ret = df["Close"].pct_change().fillna(0)
    bench_equity = initial_capital * (1 + bench_ret).cumprod()

    metrics = compute_metrics(strat_ret, position, bench_ret)

    return BacktestResult(
        ticker=ticker,
        strategy_key=strategy.key,
        strategy_name=strategy.name,
        equity_curve=equity,
        returns=strat_ret,
        positions=position,
        benchmark_equity=bench_equity,
        metrics=metrics,
    )


def leaderboard(results: list[BacktestResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        row = {"Ticker": r.ticker, "Strategy": r.strategy_name, **r.metrics}
        rows.append(row)
    return pd.DataFrame(rows)
