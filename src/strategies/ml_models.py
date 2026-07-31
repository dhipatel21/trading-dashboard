"""Classical ML strategies: tree-ensemble classifiers on engineered technical features.

This mirrors the "supervised alpha model" paradigm used by frameworks like
Microsoft Qlib — engineer features, train a classifier walk-forward, trade its
directional prediction.
"""
from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier

from .base import Strategy, register
from .features import build_feature_matrix, build_target, walk_forward_predict


def random_forest_signal(df, min_train: int = 252, refit_every: int = 21, n_estimators: int = 200):
    feats = build_feature_matrix(df)
    target = build_target(df)

    def factory():
        return RandomForestClassifier(
            n_estimators=n_estimators, max_depth=5, min_samples_leaf=20,
            random_state=42, n_jobs=-1,
        )

    return walk_forward_predict(feats, target, factory, min_train, refit_every)


def gradient_boosting_signal(df, min_train: int = 252, refit_every: int = 21):
    feats = build_feature_matrix(df)
    target = build_target(df)

    def factory():
        return HistGradientBoostingClassifier(max_depth=4, max_iter=150, learning_rate=0.08, random_state=42)

    return walk_forward_predict(feats, target, factory, min_train, refit_every)


register(Strategy(
    key="random_forest",
    name="Random Forest Alpha Model",
    category="Machine Learning",
    description="Random-forest classifier trained walk-forward on ~10 technical features "
                "(returns, RSI, MACD histogram, Bollinger z-score, volume z-score) to predict "
                "next-day direction. Refit every 21 trading days on an expanding window.",
    reference="Ensemble-tree 'alpha' models as used in Microsoft Qlib and widespread "
              "quant-research practice; Gu, Kelly & Xiu, 'Empirical Asset Pricing via "
              "Machine Learning', Review of Financial Studies (2020).",
    signal_fn=random_forest_signal,
    params={"min_train": 252, "refit_every": 21, "n_estimators": 200},
))

register(Strategy(
    key="gradient_boosting",
    name="Gradient-Boosted Trees Alpha Model",
    category="Machine Learning",
    description="Histogram gradient-boosted tree classifier (XGBoost/LightGBM-style) on the "
                "same feature set, walk-forward trained. Typically the strongest tabular "
                "baseline in modern ML competitions and quant-research benchmarks.",
    reference="Chen & Guestrin, 'XGBoost: A Scalable Tree Boosting System' (2016); "
              "Ke et al., 'LightGBM' (2017); scikit-learn HistGradientBoostingClassifier.",
    signal_fn=gradient_boosting_signal,
    params={"min_train": 252, "refit_every": 21},
))
