"""Shared feature engineering + walk-forward helper for the ML/DL/RL strategies.

All models here are trained walk-forward (expanding window, periodic refit) so
that a prediction for day t only ever uses information available through day
t-1's return — no look-ahead. The backtester then shifts signals by one more
bar before applying them, exactly as it does for the rule-based strategies.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    close = df["Close"]
    ret1 = close.pct_change()
    feats = pd.DataFrame(index=df.index)
    feats["ret_1"] = ret1
    feats["ret_5"] = close.pct_change(5)
    feats["ret_10"] = close.pct_change(10)
    feats["ret_21"] = close.pct_change(21)
    feats["vol_10"] = ret1.rolling(10).std()
    feats["vol_21"] = ret1.rolling(21).std()

    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    feats["rsi_14"] = (100 - 100 / (1 + rs)).fillna(50)

    ema_fast = close.ewm(span=12, adjust=False).mean()
    ema_slow = close.ewm(span=26, adjust=False).mean()
    macd = ema_fast - ema_slow
    feats["macd_hist"] = macd - macd.ewm(span=9, adjust=False).mean()

    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    feats["bb_z"] = (close - sma20) / std20.replace(0, np.nan)

    if "Volume" in df.columns:
        vol = df["Volume"].astype(float)
        feats["vol_z"] = (vol - vol.rolling(20).mean()) / vol.rolling(20).std().replace(0, np.nan)
    else:
        feats["vol_z"] = 0.0

    feats["sma_ratio"] = close / close.rolling(50).mean() - 1
    return feats


def build_target(df: pd.DataFrame) -> pd.Series:
    """+1 if next bar's close is higher, -1 otherwise."""
    fwd_ret = df["Close"].shift(-1) / df["Close"] - 1
    return np.sign(fwd_ret).replace(0, 1)


def walk_forward_predict(
    feats: pd.DataFrame,
    target: pd.Series,
    model_factory,
    min_train: int = 252,
    refit_every: int = 21,
) -> pd.Series:
    """Expanding-window walk-forward classification.

    At each refit point i, trains on samples [0, i) whose target is already
    known (i.e. up to i-1, since target[i-1] depends on price[i]) and predicts
    signals for [i, i + refit_every).
    """
    X = feats.values
    y = target.values
    n = len(feats)
    preds = np.zeros(n)
    valid = ~np.isnan(X).any(axis=1) & ~np.isnan(y)

    i = min_train
    last_model = None
    while i < n:
        train_idx = np.arange(0, i)
        train_mask = valid[train_idx] & (train_idx < n - 1)
        train_idx = train_idx[train_mask]
        if len(train_idx) >= 30 and len(np.unique(y[train_idx])) > 1:
            model = model_factory()
            model.fit(X[train_idx], y[train_idx])
            last_model = model
        end = min(i + refit_every, n)
        block = np.arange(i, end)
        block_valid = valid[block]
        if last_model is not None and block_valid.any():
            block_X = X[block][block_valid]
            pred = last_model.predict(block_X)
            block_preds = np.zeros(len(block))
            block_preds[block_valid] = pred
            preds[block] = block_preds
        i = end

    return pd.Series(preds, index=feats.index)


def train_final_predict_proba(
    feats: pd.DataFrame,
    target: pd.Series,
    model_factory,
    min_train: int = 30,
) -> tuple[int, float | None]:
    """Fit once on ALL rows whose target is already known, then predict the
    *next*, not-yet-realized bar from the most recent feature row.

    Returns (signal in {-1, 1}, confidence = predicted-class probability), or
    (0, None) if there isn't enough clean history to fit on yet.
    """
    X = feats.values
    y = target.values
    n = len(feats)
    valid = ~np.isnan(X).any(axis=1) & ~np.isnan(y)

    train_idx = np.arange(0, n - 1)
    train_idx = train_idx[valid[train_idx]]
    if len(train_idx) < min_train or len(np.unique(y[train_idx])) < 2:
        return 0, None
    if np.isnan(X[-1]).any():
        return 0, None

    model = model_factory()
    model.fit(X[train_idx], y[train_idx])
    last_row = X[-1:].astype(float)
    pred_label = int(model.predict(last_row)[0])
    proba = None
    if hasattr(model, "predict_proba"):
        classes = list(model.classes_)
        p = model.predict_proba(last_row)[0]
        proba = float(p[classes.index(pred_label)])
    return (1 if pred_label > 0 else -1), proba
