# Trading Strategy Lab

A live-refreshing dashboard for comparing classic technical, statistical, machine-learning,
deep-learning and reinforcement-learning trading strategies across any stocks you choose —
built on open-source tools (yfinance, scikit-learn, PyTorch, Streamlit, Plotly).

This is **not a frozen snapshot**: data is pulled on demand (yfinance, with an optional
Alpha Vantage fallback/key), cached for only 20–60 seconds, and there's a live auto-refreshing
quote view alongside the backtests.

## Quickstart

```bash
cd trading-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## What's in the strategy library

| Category | Strategy | Idea |
|---|---|---|
| Trend Following | SMA Crossover (Golden/Death Cross) | Long when 50-day SMA > 200-day SMA |
| Trend Following | MACD Trend/Momentum | Long when MACD line > signal line |
| Trend Following | Donchian Channel Breakout (Turtle) | Long on 20-day high breakout, exit on 10-day low |
| Mean Reversion | RSI Oversold/Overbought | Buy RSI < 30, exit RSI > 70 |
| Mean Reversion | Bollinger Band Reversion | Buy below lower band, exit at the mean |
| Mean Reversion / Statistical | Rolling Z-Score Reversion | Trade the z-score of price vs its own rolling distribution |
| Momentum | Time-Series Momentum (12-1) | Long/short on trailing 6-month return sign |
| Momentum | Volatility-Managed Momentum | Time-series momentum, stands aside in high-vol regimes |
| Machine Learning | Random Forest Alpha Model | Walk-forward RF classifier on technical features |
| Machine Learning | Gradient-Boosted Trees Alpha Model | Walk-forward HistGBM classifier (XGBoost/LightGBM-style) |
| Deep Learning | LSTM Sequence Model | Small LSTM over a 20-day feature window, retrained walk-forward |
| Reinforcement Learning | Q-Learning RL Agent | Tabular RL agent (RSI/momentum/position state), FinRL-style reward |
| Benchmark | Buy & Hold | The baseline everything else must beat |

Every strategy is trained/signaled **walk-forward** — no look-ahead: a model only ever sees
data through day *t-1* when deciding day *t*'s position, and the backtester applies that
position starting the following bar's return.

Full descriptions + academic/open-source references are in the app's **Methodology** tab.

## Dashboard tabs

- **Live Market** — quotes + intraday sparklines for every ticker you add, with an optional
  auto-refresh (off by default — see note below).
- **Backtest & Equity Curves** — indexed (base = 100) equity curves per strategy for a focus ticker.
- **Model Comparison** — Sharpe-ratio heatmap (strategy × ticker), average-Sharpe ranking,
  best-model-per-ticker leaderboard, full metrics table (CAGR, Sharpe, Sortino, Max Drawdown,
  Calmar, Win Rate, # Trades, excess return vs. buy & hold).
- **Deep Dive** — equity curve, drawdown, rolling Sharpe, and trade log for one ticker+model.
- **Predictions** — what every model says to do *right now*: each strategy refits on all
  available history through the latest close and predicts the next, not-yet-realized bar.
  ML/DL models (Random Forest, Gradient Boosting, LSTM) report a genuine confidence
  (predicted-class probability); rule-based models show signal only. Also scans a configurable
  universe of tickers and ranks the top 10 each model currently favors long.
- **Elliott Wave** — a full ZigZag pivot / impulse-correction / Fibonacci-cascade engine with a
  walk-forward accuracy backtest and a composite "Top Setups" screener, all running live on
  whatever ticker you pick (no embedded snapshot, no third-party connector). Includes the
  original family-chat call log, playbook and methodology write-up this feature is based on.
  See `src/elliott_wave.py` for the algorithm and `src/ew_content.py` for the static content.
- **Methodology** — every strategy's description, reference, and the backtest assumptions.

> **Auto-refresh note**: the "Auto-refresh live prices" toggle on the Live Market tab reruns
> the *entire* app on a timer (a Streamlit limitation — it can't refresh just one tab). Leave
> it off while running a backtest or a Predictions universe scan, or it'll cancel the
> in-progress computation before it finishes.

## Data sources

- **yfinance** (default): free, no API key, scrapes Yahoo Finance. Good for daily history and
  ~15-min-delayed intraday quotes.
- **Alpha Vantage** (optional fallback or primary): get a free key at
  https://www.alphavantage.co/support/#api-key, paste it in the sidebar (or set
  `ALPHAVANTAGE_API_KEY` in a `.env`/shell env var). Free tier is rate-limited (5 calls/min,
  25/day) — useful as a backup when yfinance is rate-limited, or for fundamentals/news-sentiment
  extensions later.

## Adding your own strategy

1. Add a function `my_strategy(df, **params) -> pd.Series` returning values in `{-1, 0, 1}`
   to a file under `src/strategies/`.
2. Register it: `register(Strategy(key=..., name=..., category=..., description=...,
   reference=..., signal_fn=my_strategy, params={...}))`.
3. Import that module in `src/strategies/__init__.py`.

It will automatically show up in the sidebar's strategy multiselect and in every comparison view.

## Notes / limitations

- Educational tool, **not investment advice**. Backtests use a flat transaction-cost
  assumption and no slippage/market-impact model.
- ML/DL/RL models are intentionally small so they can retrain interactively; on long
  histories (5–10y) the LSTM and Q-learning strategies take longer to run — a progress bar
  shows status while backtests compute.
- yfinance occasionally rate-limits or has outages; that's what the Alpha Vantage fallback
  is for.
