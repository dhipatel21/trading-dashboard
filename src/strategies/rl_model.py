"""Reinforcement-learning strategy: tabular Q-learning agent.

A lightweight, dependency-free (no gym/stable-baselines) RL agent in the
spirit of FinRL-style trading agents. State = discretized (RSI, momentum,
current position). Action = target position in {short, flat, long}. Reward
= next-bar P&L minus a small transaction cost for changing position.
Retrained (continued) walk-forward on an expanding window, acted on greedily
out-of-sample.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Strategy, register
from .features import build_feature_matrix

ACTIONS = [-1, 0, 1]
N_RSI_BINS = 5
N_MOM_BINS = 5
N_POS = 3  # -1, 0, 1 -> index 0,1,2


def _discretize(feats: pd.DataFrame) -> np.ndarray:
    rsi = feats["rsi_14"].fillna(50)
    mom = feats["ret_21"].fillna(0)
    rsi_bin = pd.cut(rsi, bins=[-1, 20, 40, 60, 80, 101], labels=False)
    mom_q = mom.rolling(252, min_periods=30).quantile
    lo = mom.rolling(252, min_periods=30).apply(lambda x: np.quantile(x, 0.2), raw=True)
    hi = mom.rolling(252, min_periods=30).apply(lambda x: np.quantile(x, 0.8), raw=True)
    mom_bin = pd.Series(2, index=feats.index)
    mom_bin[mom < lo] = 0
    mom_bin[(mom >= lo) & (mom < mom.rolling(252, min_periods=30).median())] = 1
    mom_bin[(mom > mom.rolling(252, min_periods=30).median()) & (mom <= hi)] = 3
    mom_bin[mom > hi] = 4
    return np.stack([rsi_bin.fillna(2).astype(int).values, mom_bin.astype(int).values], axis=1)


def q_learning_signal(
    df: pd.DataFrame,
    min_train: int = 252,
    refit_every: int = 21,
    epochs: int = 3,
    alpha: float = 0.2,
    gamma: float = 0.9,
    epsilon: float = 0.15,
    cost: float = 0.0005,
) -> pd.Series:
    feats = build_feature_matrix(df)
    close = df["Close"].values
    rets = np.zeros(len(df))
    rets[:-1] = close[1:] / close[:-1] - 1
    disc = _discretize(feats)
    n = len(df)

    Q = np.zeros((N_RSI_BINS + 1, N_MOM_BINS + 1, N_POS, len(ACTIONS)))
    rng = np.random.default_rng(42)
    preds = np.zeros(n)
    pos_idx = 1  # start flat

    def state_idx(t, pos_idx):
        r, m = disc[t]
        r = min(max(r, 0), N_RSI_BINS)
        m = min(max(m, 0), N_MOM_BINS)
        return r, m, pos_idx

    i = min_train
    while i < n:
        # Train on expanding window [0, i) with several epochs of epsilon-greedy Q-learning.
        for _ in range(epochs):
            pidx = 1
            for t in range(1, i - 1):
                s = state_idx(t, pidx)
                if rng.random() < epsilon:
                    a_idx = rng.integers(0, len(ACTIONS))
                else:
                    a_idx = int(np.argmax(Q[s]))
                action = ACTIONS[a_idx]
                new_pidx = action + 1
                reward = action * rets[t] - cost * abs(action - ACTIONS[pidx - 1])
                s_next = state_idx(t + 1, new_pidx)
                best_next = np.max(Q[s_next])
                Q[s][a_idx] += alpha * (reward + gamma * best_next - Q[s][a_idx])
                pidx = new_pidx

        # Act greedily out-of-sample for [i, i+refit_every)
        end = min(i + refit_every, n)
        pidx = pos_idx
        for t in range(i, end):
            s = state_idx(t, pidx)
            a_idx = int(np.argmax(Q[s]))
            action = ACTIONS[a_idx]
            preds[t] = action
            pidx = action + 1
        pos_idx = pidx
        i = end

    return pd.Series(preds, index=df.index)


register(Strategy(
    key="q_learning",
    name="Q-Learning RL Agent",
    category="Reinforcement Learning",
    description="Tabular Q-learning agent whose state is a discretized (RSI, 21-day "
                "momentum, current position) and whose actions are target long/flat/short "
                "positions, rewarded on next-bar P&L net of transaction cost. Retrained on "
                "an expanding window and acted on greedily out-of-sample — the same "
                "state/action/reward framing used by FinRL-style trading agents.",
    reference="AI4Finance-Foundation, 'FinRL: Deep Reinforcement Learning Framework for "
              "Quantitative Trading' (github.com/AI4Finance-Foundation/FinRL); "
              "Sutton & Barto, 'Reinforcement Learning: An Introduction'.",
    signal_fn=q_learning_signal,
    params={"min_train": 252, "refit_every": 21, "epochs": 3},
))
