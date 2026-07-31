"""Deep-learning strategy: a small LSTM sequence classifier.

Deep sequence models (LSTM / Transformer variants) are the current research
frontier for price-direction forecasting (see references below). This is a
deliberately small, fast LSTM — a few thousand parameters — trained
walk-forward so it can realistically refit inside an interactive dashboard.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from .base import Strategy, register
from .features import build_feature_matrix, build_target


class _TinyLSTM(nn.Module):
    def __init__(self, n_features: int, hidden: int = 16):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, batch_first=True)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :]).squeeze(-1)


def _make_sequences(X: np.ndarray, y: np.ndarray, seq_len: int):
    xs, ys = [], []
    for i in range(seq_len, len(X)):
        xs.append(X[i - seq_len:i])
        ys.append(y[i - 1])
    if not xs:
        return np.empty((0, seq_len, X.shape[1])), np.empty((0,))
    return np.stack(xs), np.array(ys)


def lstm_signal(
    df: pd.DataFrame,
    seq_len: int = 20,
    min_train: int = 252,
    refit_every: int = 63,
    epochs: int = 15,
    hidden: int = 16,
) -> pd.Series:
    feats = build_feature_matrix(df)
    target = build_target(df)

    means = feats.rolling(252, min_periods=30).mean()
    stds = feats.rolling(252, min_periods=30).std().replace(0, np.nan)
    norm_feats = ((feats - means) / stds).fillna(0.0).clip(-5, 5)

    X_all = norm_feats.values.astype(np.float32)
    y_all = target.values.astype(np.float32)
    valid = ~np.isnan(X_all).any(axis=1) & ~np.isnan(y_all)

    n = len(feats)
    preds = np.zeros(n)
    torch.manual_seed(42)

    i = min_train
    model = None
    while i < n:
        train_mask = valid[:i].copy()
        train_mask[max(0, i - 1):] = False  # never train on a target we can't know yet
        X_train_raw = X_all[:i][train_mask[:i]]
        y_train_raw = y_all[:i][train_mask[:i]]

        if len(X_train_raw) >= seq_len + 30:
            Xs, ys = _make_sequences(X_train_raw, y_train_raw, seq_len)
            ys_bin = (ys > 0).astype(np.float32)
            if len(np.unique(ys_bin)) > 1:
                model = _TinyLSTM(n_features=X_all.shape[1], hidden=hidden)
                opt = torch.optim.Adam(model.parameters(), lr=1e-3)
                loss_fn = nn.BCEWithLogitsLoss()
                xt = torch.tensor(Xs)
                yt = torch.tensor(ys_bin)
                model.train()
                for _ in range(epochs):
                    opt.zero_grad()
                    out = model(xt)
                    loss = loss_fn(out, yt)
                    loss.backward()
                    opt.step()

        end = min(i + refit_every, n)
        if model is not None:
            model.eval()
            for j in range(i, end):
                if j - seq_len < 0 or not valid[j - seq_len:j].all():
                    continue
                window = X_all[j - seq_len:j][None, :, :]
                with torch.no_grad():
                    logit = model(torch.tensor(window)).item()
                preds[j] = 1.0 if logit > 0 else -1.0
        i = end

    return pd.Series(preds, index=feats.index)


register(Strategy(
    key="lstm",
    name="LSTM Sequence Model",
    category="Deep Learning",
    description="A compact LSTM reads the last 20 days of engineered features and predicts "
                "next-day direction. Retrained walk-forward every ~quarter on an expanding "
                "window. Deep sequence models like this are the current research frontier "
                "for price-direction forecasting.",
    reference="Fischer & Krauss, 'Deep learning with long short-term memory networks for "
              "financial market predictions', European Journal of Operational Research (2018); "
              "'Transformers versus LSTMs for electronic trading' (arXiv:2309.11400, 2024).",
    signal_fn=lstm_signal,
    params={"seq_len": 20, "min_train": 252, "refit_every": 63, "epochs": 15, "hidden": 16},
))
