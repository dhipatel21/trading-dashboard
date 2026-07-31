"""
Multi-Strategy Trading Dashboard
=================================
Compare classic technical, statistical, ML, deep-learning and reinforcement-
learning trading strategies across any tickers you choose — against live and
historical data pulled on demand (not a frozen snapshot).

Run with:  streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from src.data_feed import get_history, get_live_quotes
from src.strategies import all_strategies, get as get_strategy
from src.backtest import backtest_strategy, leaderboard
from src.theme import register_template, CATEGORICAL, DIVERGING, GOOD, CRITICAL
from src.ui import inject_css, page_header, category_chip

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

st.set_page_config(page_title="Trading Strategy Lab", layout="wide")
register_template()
inject_css()

DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "SPY"]
PERIOD_OPTIONS = {"6 months": "6mo", "1 year": "1y", "2 years": "2y", "5 years": "5y", "10 years": "10y", "Max": "max"}

# Curated, liquid large-caps across sectors + two index ETFs. This is the full
# selectable pool for a universe scan — big enough to be interesting, but NOT
# the default selection (see DEFAULT_SCAN_UNIVERSE below): scanning all 40 against
# several models means dozens of fresh network fetches, which can take minutes.
DEFAULT_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    "JPM", "V", "MA", "UNH", "JNJ", "PG", "HD", "XOM",
    "CVX", "BAC", "WMT", "KO", "PEP", "COST", "ADBE", "CRM",
    "AMD", "NFLX", "DIS", "PFE", "MRK", "ORCL", "IBM", "GE",
    "CAT", "BA", "INTC", "QCOM", "T", "VZ", "SPY", "QQQ",
]

# Small, fast defaults so "Run Universe Scan" feels responsive out of the box.
# Users can expand either multiselect for a broader (slower) scan.
DEFAULT_SCAN_UNIVERSE = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "SPY", "QQQ"]
DEFAULT_SCAN_STRATEGIES = ["buy_and_hold", "sma_crossover", "rsi_mean_reversion", "random_forest"]

SIGNAL_LABELS = {1: "LONG", 0: "FLAT", -1: "SHORT"}


def _style_signal(v):
    color = {"LONG": GOOD, "SHORT": CRITICAL, "FLAT": "#898781"}.get(v, "#898781")
    return f"color: {color}; font-weight: 700;"

# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
if "tickers" not in st.session_state:
    st.session_state.tickers = DEFAULT_TICKERS.copy()
if "av_api_key" not in st.session_state:
    st.session_state.av_api_key = ""

STRATS = all_strategies()
STRAT_BY_KEY = {s.key: s for s in STRATS}
CATEGORY_ORDER = ["Trend Following", "Mean Reversion", "Mean Reversion / Statistical",
                   "Momentum", "Machine Learning", "Deep Learning", "Reinforcement Learning", "Benchmark"]


# ----------------------------------------------------------------------------
# Sidebar — controls
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Strategy Lab")
    st.caption("Configure tickers, models & data source below.")
    st.divider()

    st.subheader("Tickers")
    new_ticker = st.text_input("Add a ticker (e.g. TSLA)", value="", key="add_ticker").strip().upper()
    add_col1, add_col2 = st.columns([1, 1])
    if add_col1.button("Add", width="stretch") and new_ticker:
        if new_ticker not in st.session_state.tickers:
            st.session_state.tickers.append(new_ticker)
    if add_col2.button("Reset list", width="stretch"):
        st.session_state.tickers = DEFAULT_TICKERS.copy()

    tickers = st.multiselect(
        "Tickers to compare", options=sorted(set(st.session_state.tickers + DEFAULT_TICKERS)),
        default=st.session_state.tickers, key="ticker_select",
    )
    st.session_state.tickers = tickers

    st.subheader("Backtest window")
    period_label = st.selectbox("History length", list(PERIOD_OPTIONS.keys()), index=2)
    period = PERIOD_OPTIONS[period_label]

    st.subheader("Strategies")
    strat_labels = {f"{s.name} ({s.category})": s.key for s in STRATS}
    default_keys = ["buy_and_hold", "sma_crossover", "rsi_mean_reversion", "time_series_momentum",
                    "random_forest", "lstm", "q_learning"]
    default_labels = [lbl for lbl, k in strat_labels.items() if k in default_keys]
    chosen_labels = st.multiselect("Models to run", options=list(strat_labels.keys()), default=default_labels)
    chosen_keys = [strat_labels[l] for l in chosen_labels]

    st.subheader("Assumptions")
    cost_bps = st.slider("Transaction cost (bps per trade)", 0, 50, 5)
    capital = st.number_input("Initial capital ($)", min_value=100, value=10_000, step=100)

    st.subheader("Data source")
    prefer_source = st.radio("Primary source", ["yfinance (free)", "Alpha Vantage"], index=0)
    prefer_source_key = "yfinance" if prefer_source.startswith("yfinance") else "alpha_vantage"
    av_key_input = st.text_input("Alpha Vantage API key (optional fallback)", type="password",
                                  value=st.session_state.av_api_key,
                                  help="Free key from alphavantage.co. Used automatically if yfinance "
                                       "fails/rate-limits, or as primary if selected above.")
    st.session_state.av_api_key = av_key_input

    st.subheader("Live view")
    live_auto = st.checkbox("Auto-refresh live prices", value=False)
    live_interval = st.slider("Refresh every (seconds)", 2, 60, 5, disabled=not HAS_AUTOREFRESH)
    if not HAS_AUTOREFRESH:
        st.caption("Install `streamlit-autorefresh` for automatic polling; use the manual refresh button below for now.")
    elif live_auto:
        st.caption("Note: auto-refresh reruns the whole app on a timer, which will interrupt any "
                   "in-progress backtest or universe scan before it finishes. Turn it off while running those.")

    run_clicked = st.button("Run / Refresh Backtests", type="primary", width="stretch")


# ----------------------------------------------------------------------------
# Cached compute
# ----------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def cached_backtest(ticker: str, period: str, strategy_key: str, cost_bps: float, capital: float, prefer: str):
    df, source = get_history(ticker, period=period, interval="1d", prefer=prefer)
    if df.empty or len(df) < 60:
        return None, source
    strategy = get_strategy(strategy_key)
    result = backtest_strategy(df, strategy, ticker, cost_bps=cost_bps, initial_capital=capital)
    return result, source


def run_all(tickers, strategy_keys, period, cost_bps, capital, prefer):
    results = {}
    sources = {}
    total = len(tickers) * len(strategy_keys)
    if total == 0:
        return results, sources
    progress = st.progress(0.0, text="Running backtests…")
    done = 0
    for t in tickers:
        for sk in strategy_keys:
            res, source = cached_backtest(t, period, sk, cost_bps, capital, prefer)
            if res is not None:
                results[(t, sk)] = res
                sources[t] = source
            done += 1
            progress.progress(done / total, text=f"Running backtests… {t} / {STRAT_BY_KEY[sk].name}")
    progress.empty()
    return results, sources


@st.cache_data(ttl=300, show_spinner=False)
def cached_prediction(ticker: str, period: str, strategy_key: str, prefer: str):
    df, source = get_history(ticker, period=period, interval="1d", prefer=prefer)
    if df.empty or len(df) < 60:
        return None
    strategy = get_strategy(strategy_key)
    pred = strategy.predict_latest(df)
    momentum_21d = float(df["Close"].pct_change(21).iloc[-1]) if len(df) > 21 else None
    return {
        "ticker": ticker,
        "strategy_key": strategy_key,
        "signal": pred["signal"],
        "confidence": pred["confidence"],
        "momentum_21d": momentum_21d,
        "price": float(df["Close"].iloc[-1]),
        "as_of": df.index[-1],
        "source": source,
    }


def run_predictions(tickers, strategy_keys, period, prefer, label="Running predictions"):
    preds = {}
    total = len(tickers) * len(strategy_keys)
    if total == 0:
        return preds
    progress = st.progress(0.0, text=f"{label}… 0/{total}")
    done = 0
    for t in tickers:
        for sk in strategy_keys:
            p = cached_prediction(t, period, sk, prefer)
            if p is not None:
                preds[(t, sk)] = p
            done += 1
            progress.progress(done / total, text=f"{label}… {done}/{total} · {t} / {STRAT_BY_KEY[sk].name}")
    progress.empty()
    return preds


# ----------------------------------------------------------------------------
# Header + tabs
# ----------------------------------------------------------------------------
page_header(
    "Trading Strategy Lab",
    f"Comparing {len(STRATS)} strategies — trend, mean-reversion, momentum, ML, deep learning "
    "and reinforcement learning — across live and historical stock data. Nothing here is a "
    "frozen snapshot: prices refresh on demand and every model retrains walk-forward.",
)

tab_live, tab_backtest, tab_compare, tab_deep, tab_predict, tab_about = st.tabs(
    ["Live Market", "Backtest & Equity Curves", "Model Comparison", "Deep Dive", "Predictions", "Methodology"]
)

# ---- Live Market -------------------------------------------------------
with tab_live:
    st.subheader("Live quotes")

    if HAS_AUTOREFRESH and live_auto:
        st_autorefresh(interval=live_interval * 1000, key="live_autorefresh")
    manual_refresh = st.button("Refresh now")

    if tickers:
        quotes = get_live_quotes(tickers)
        if not quotes.empty:
            def _style_change(v):
                if pd.isna(v):
                    return ""
                color = GOOD if v >= 0 else CRITICAL
                return f"color: {color}; font-weight: 600;"

            show_cols = ["ticker", "price", "change", "change_pct", "day_high", "day_low", "volume", "as_of"]
            styled = quotes[show_cols].style.format({
                "price": lambda x: f"${x:,.2f}" if pd.notna(x) else "—",
                "change": lambda x: f"{x:+.2f}" if pd.notna(x) else "—",
                "change_pct": lambda x: f"{x:+.2f}%" if pd.notna(x) else "—",
                "day_high": lambda x: f"${x:,.2f}" if pd.notna(x) else "—",
                "day_low": lambda x: f"${x:,.2f}" if pd.notna(x) else "—",
                "volume": lambda x: f"{x:,.0f}" if pd.notna(x) else "—",
                "as_of": lambda x: x.strftime("%H:%M:%S"),
            }).map(_style_change, subset=["change", "change_pct"])
            st.dataframe(styled, width="stretch", hide_index=True)
        st.caption(f"Last pulled: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

        st.subheader("Intraday snapshot")
        cols = st.columns(min(len(tickers), 4) or 1)
        for i, t in enumerate(tickers):
            with cols[i % len(cols)]:
                try:
                    intraday, src = get_history(t, period="1d", interval="5m", prefer=prefer_source_key)
                except Exception as e:  # noqa: BLE001
                    intraday, src = pd.DataFrame(), "error"
                if not intraday.empty:
                    fig = go.Figure(go.Scatter(x=intraday.index, y=intraday["Close"], mode="lines",
                                                line=dict(width=2, color=CATEGORICAL[0])))
                    fig.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), title=f"{t} · today ({src})",
                                       showlegend=False, xaxis_visible=False)
                    fig.update_yaxes(autorange=True)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info(f"No intraday data for {t} (market may be closed).")
    else:
        st.info("Add at least one ticker in the sidebar.")

# ---- Backtest & Equity Curves -------------------------------------------
with tab_backtest:
    if not tickers or not chosen_keys:
        st.info("Pick at least one ticker and one strategy in the sidebar, then click **Run / Refresh Backtests**.")
    else:
        if run_clicked or "results" not in st.session_state:
            results, sources = run_all(tickers, chosen_keys, period, cost_bps, capital, prefer_source_key)
            st.session_state.results = results
            st.session_state.sources = sources
        results = st.session_state.get("results", {})
        sources = st.session_state.get("sources", {})

        if results:
            focus_ticker = st.selectbox("Focus ticker", tickers)
            st.caption(f"Data source used: **{sources.get(focus_ticker, 'n/a')}**")

            fig = go.Figure()
            any_added = False
            for idx, sk in enumerate(chosen_keys):
                res = results.get((focus_ticker, sk))
                if res is None:
                    continue
                norm = res.equity_curve / res.equity_curve.iloc[0] * 100
                fig.add_trace(go.Scatter(x=norm.index, y=norm.values, mode="lines", name=res.strategy_name,
                                          line=dict(width=2, color=CATEGORICAL[idx % len(CATEGORICAL)])))
                any_added = True
            if any_added:
                bench = next((r for (t, k), r in results.items() if t == focus_ticker), None)
                if bench is not None:
                    bnorm = bench.benchmark_equity / bench.benchmark_equity.iloc[0] * 100
                    fig.add_trace(go.Scatter(x=bnorm.index, y=bnorm.values, mode="lines", name=f"{focus_ticker} Buy & Hold",
                                              line=dict(width=1.5, color="#898781", dash="dot")))
                fig.update_layout(title=f"{focus_ticker} — Indexed Strategy Performance (Base = 100)",
                                   yaxis_title="Index (base = 100)",
                                   legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
                                   margin=dict(r=170))
                st.plotly_chart(fig, use_container_width=True)

            lb_rows = [r for r in results.values()]
            lb_df = leaderboard(lb_rows)
            focus_lb = lb_df[lb_df["Ticker"] == focus_ticker].sort_values("Sharpe", ascending=False)
            fmt = {"Total Return": "{:+.1%}", "CAGR": "{:+.1%}", "Ann. Volatility": "{:.1%}", "Sharpe": "{:.2f}",
                   "Sortino": "{:.2f}", "Max Drawdown": "{:.1%}", "Calmar": "{:.2f}", "Win Rate": "{:.1%}",
                   "Benchmark Return": "{:+.1%}", "Excess vs Benchmark": "{:+.1%}"}
            st.dataframe(focus_lb.style.format(fmt), width="stretch", hide_index=True)
        else:
            st.warning("No results yet — no tickers returned usable data. Try yfinance for a common ticker like AAPL.")

# ---- Model Comparison ----------------------------------------------------
with tab_compare:
    results = st.session_state.get("results", {})
    if not results:
        st.info("Run backtests first (Backtest & Equity Curves tab, or the sidebar button).")
    else:
        lb_df = leaderboard(list(results.values()))

        st.subheader("Sharpe ratio — strategy × ticker")
        pivot = lb_df.pivot_table(index="Strategy", columns="Ticker", values="Sharpe")
        heat = go.Figure(go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index,
            colorscale=[[0, "#8a1f1f"], [0.5, "#383835"], [1, "#184f95"]],
            zmid=0, colorbar=dict(title="Sharpe"),
            text=[[f"{v:.2f}" if pd.notna(v) else "" for v in row] for row in pivot.values],
            texttemplate="%{text}",
        ))
        heat.update_layout(height=120 + 30 * len(pivot.index), margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(heat, use_container_width=True)

        st.subheader("Average Sharpe ratio by strategy (across selected tickers)")
        avg_sharpe = lb_df.groupby("Strategy")["Sharpe"].mean().sort_values(ascending=False)
        bar = go.Figure(go.Bar(x=avg_sharpe.values, y=avg_sharpe.index, orientation="h",
                                marker_color=[GOOD if v >= 0 else CRITICAL for v in avg_sharpe.values]))
        bar.update_layout(height=100 + 30 * len(avg_sharpe), xaxis_title="Mean Sharpe", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(bar, use_container_width=True)

        st.subheader("Best model per ticker")
        best = lb_df.loc[lb_df.groupby("Ticker")["Sharpe"].idxmax()][["Ticker", "Strategy", "Sharpe", "CAGR", "Max Drawdown"]]
        st.dataframe(best.style.format({"Sharpe": "{:.2f}", "CAGR": "{:+.1%}", "Max Drawdown": "{:.1%}"}),
                     width="stretch", hide_index=True)

        st.subheader("Full comparison table")
        fmt = {"Total Return": "{:+.1%}", "CAGR": "{:+.1%}", "Ann. Volatility": "{:.1%}", "Sharpe": "{:.2f}",
               "Sortino": "{:.2f}", "Max Drawdown": "{:.1%}", "Calmar": "{:.2f}", "Win Rate": "{:.1%}",
               "Benchmark Return": "{:+.1%}", "Excess vs Benchmark": "{:+.1%}"}
        st.dataframe(lb_df.sort_values(["Ticker", "Sharpe"], ascending=[True, False]).style.format(fmt),
                     width="stretch", hide_index=True)

# ---- Deep Dive ------------------------------------------------------------
with tab_deep:
    results = st.session_state.get("results", {})
    if not results:
        st.info("Run backtests first.")
    else:
        combo_options = {f"{t} — {STRAT_BY_KEY[k].name}": (t, k) for (t, k) in results.keys()}
        chosen = st.selectbox("Ticker + strategy", list(combo_options.keys()))
        t, k = combo_options[chosen]
        res = results[(t, k)]

        strat = STRAT_BY_KEY[k]
        st.markdown(f"**{strat.name}** · _{strat.category}_")
        st.caption(strat.description)
        st.caption(f"Reference: {strat.reference}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CAGR", f"{res.metrics['CAGR']:+.1%}")
        m2.metric("Sharpe", f"{res.metrics['Sharpe']:.2f}")
        m3.metric("Max Drawdown", f"{res.metrics['Max Drawdown']:.1%}")
        m4.metric("# Trades", f"{res.metrics['# Trades']:.0f}")

        eq = res.equity_curve
        bench = res.benchmark_equity / res.benchmark_equity.iloc[0] * eq.iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=eq.index, y=eq.values, name=strat.name, line=dict(color=CATEGORICAL[0], width=2)))
        fig.add_trace(go.Scatter(x=bench.index, y=bench.values, name="Buy & Hold", line=dict(color="#898781", width=1.5, dash="dot")))
        fig.update_layout(title="Equity curve", yaxis_title="Portfolio value ($)")
        st.plotly_chart(fig, use_container_width=True)

        running_max = eq.cummax()
        dd = (eq / running_max - 1) * 100
        dd_fig = go.Figure(go.Scatter(x=dd.index, y=dd.values, fill="tozeroy", line=dict(color=CRITICAL, width=1.5),
                                       fillcolor="rgba(230,103,103,0.15)"))
        dd_fig.update_layout(title="Drawdown (%)", yaxis_title="Drawdown %")
        st.plotly_chart(dd_fig, use_container_width=True)

        roll_sharpe = (res.returns.rolling(63).mean() / res.returns.rolling(63).std()) * (252 ** 0.5)
        rs_fig = go.Figure(go.Scatter(x=roll_sharpe.index, y=roll_sharpe.values, line=dict(color=CATEGORICAL[6], width=1.5)))
        rs_fig.add_hline(y=0, line_color="#898781", line_width=1)
        rs_fig.update_layout(title="Rolling 63-day Sharpe", yaxis_title="Sharpe")
        st.plotly_chart(rs_fig, use_container_width=True)

        trades = res.positions[res.positions.diff().fillna(res.positions.iloc[0]) != 0]
        if not trades.empty:
            st.subheader("Position changes")
            st.dataframe(trades.rename("Position").to_frame().tail(50), width="stretch")

# ---- Predictions ------------------------------------------------------------
with tab_predict:
    st.subheader("Live model predictions")
    st.caption("Each model refits on all available history through the latest close and predicts "
               "the next, not-yet-realized bar. ML/DL models show a genuine confidence "
               "(predicted-class probability); rule-based models don't produce one. Not investment advice.")

    if not tickers or not chosen_keys:
        st.info("Pick at least one ticker and one strategy in the sidebar.")
    else:
        predict_clicked = st.button("Run Predictions", type="primary", key="run_predictions_btn")
        if predict_clicked or "predictions" not in st.session_state:
            st.session_state.predictions = run_predictions(tickers, chosen_keys, period, prefer_source_key)
        predictions = st.session_state.get("predictions", {})

        if predictions:
            rows = [{
                "Ticker": t, "Strategy": STRAT_BY_KEY[sk].name, "Signal": SIGNAL_LABELS[p["signal"]],
                "Confidence": p["confidence"], "21D Momentum": p["momentum_21d"],
                "Last Price": p["price"], "As Of": p["as_of"], "Source": p["source"],
            } for (t, sk), p in predictions.items()]
            pred_df = pd.DataFrame(rows).sort_values(["Ticker", "Strategy"])
            # Bake display strings in before styling — Streamlit's dataframe grid renders
            # NaN/None cells as the literal text "None", ignoring Styler.format for them.
            pred_df["Confidence"] = pred_df["Confidence"].map(lambda x: f"{x:.0%}" if pd.notna(x) else "—")
            pred_df["21D Momentum"] = pred_df["21D Momentum"].map(lambda x: f"{x:+.1%}" if pd.notna(x) else "—")
            pred_df["Last Price"] = pred_df["Last Price"].map(lambda x: f"${x:,.2f}")
            pred_df["As Of"] = pred_df["As Of"].map(lambda x: x.strftime("%Y-%m-%d"))

            styled = pred_df.style.map(_style_signal, subset=["Signal"])
            st.dataframe(styled, width="stretch", hide_index=True)
        else:
            st.info("Click **Run Predictions** to compute current model calls.")

    st.divider()
    st.subheader("Top 10 stocks by model")
    st.caption("Scans a broader universe and ranks the tickers each model currently favors long — "
               "by confidence for ML/DL models, by 21-day momentum as a tiebreaker (or primary "
               "ranking) for rule-based models.")

    scan_universe = st.multiselect(
        "Universe to scan", options=sorted(set(DEFAULT_UNIVERSE + tickers)),
        default=DEFAULT_SCAN_UNIVERSE, key="scan_universe",
        help="Defaults to a small, fast set. Add more tickers for a broader scan — "
             "each one is a fresh network fetch, so a bigger universe takes longer.",
    )
    rank_strat_labels = st.multiselect(
        "Models to rank", options=list(strat_labels.keys()),
        default=[lbl for lbl, k in strat_labels.items() if k in DEFAULT_SCAN_STRATEGIES],
        key="rank_strats",
    )
    rank_keys = [strat_labels[l] for l in rank_strat_labels]

    n_combos = len(scan_universe) * len(rank_keys)
    if n_combos:
        est_note = " — cached results (last 5 min) return instantly" if n_combos else ""
        st.caption(f"This scan will run {len(scan_universe)} tickers × {len(rank_keys)} models "
                   f"= {n_combos} predictions{est_note}.")

    scan_clicked = st.button("Run Universe Scan", key="run_scan_btn")
    if scan_clicked:
        st.session_state.universe_predictions = run_predictions(
            scan_universe, rank_keys, period, prefer_source_key, label="Scanning universe",
        )
    universe_predictions = st.session_state.get("universe_predictions", {})

    if universe_predictions:
        for sk in rank_keys:
            strat = STRAT_BY_KEY[sk]
            rows = [p for (t, k), p in universe_predictions.items() if k == sk]
            if not rows:
                continue
            df_rank = pd.DataFrame(rows).sort_values(
                by=["signal", "confidence", "momentum_21d"],
                ascending=[False, False, False],
                na_position="last",
            )
            top10 = df_rank.head(10)[["ticker", "signal", "confidence", "momentum_21d", "price"]].copy()
            top10["signal"] = top10["signal"].map(SIGNAL_LABELS)
            top10.columns = ["Ticker", "Signal", "Confidence", "21D Momentum", "Last Price"]
            # Bake display strings in before styling — see note above on Streamlit's null rendering.
            top10["Confidence"] = top10["Confidence"].map(lambda x: f"{x:.0%}" if pd.notna(x) else "—")
            top10["21D Momentum"] = top10["21D Momentum"].map(lambda x: f"{x:+.1%}" if pd.notna(x) else "—")
            top10["Last Price"] = top10["Last Price"].map(lambda x: f"${x:,.2f}")

            st.markdown(f"**{strat.name}** · _{strat.category}_")
            styled_top = top10.style.map(_style_signal, subset=["Signal"])
            st.dataframe(styled_top, width="stretch", hide_index=True)
    else:
        st.info("Click **Run Universe Scan** to rank the universe for each selected model.")

# ---- Methodology ----------------------------------------------------------
with tab_about:
    st.subheader("Strategy library")
    for cat in CATEGORY_ORDER:
        cat_strats = [s for s in STRATS if s.category == cat]
        if not cat_strats:
            continue
        st.markdown(category_chip(cat), unsafe_allow_html=True)
        for s in cat_strats:
            with st.expander(s.name):
                st.write(s.description)
                st.caption(f"Reference: {s.reference}")
                if s.params:
                    st.code(str(s.params), language="python")

    st.subheader("How the backtest works")
    st.markdown("""
- **No look-ahead**: every signal computed from data through day *t* is executed starting
  day *t+1*'s return. ML/DL/RL models are trained **walk-forward** (expanding window,
  periodic refit) — they only ever train on data that would have been available at the time.
- **Transaction costs**: a flat per-trade cost (basis points, configurable in the sidebar) is
  charged whenever a strategy changes its position.
- **Data**: pulled live via `yfinance` (free, no key) with an optional Alpha Vantage fallback.
  Historical caches expire every 60s (daily bars) / 5s (live quotes) so results reflect
  current data, not a frozen snapshot.
- **Predictions tab**: separate from backtesting. Each model does one *final* fit on all
  history through today's close and predicts the next, not-yet-realized bar — this is a
  genuine forecast, not a backtested result. Random Forest, Gradient Boosting and the LSTM
  report a real confidence (predicted-class probability); rule-based and RL strategies show
  signal only. The universe scan runs this once per ticker × model, so a bigger universe or
  more models takes longer — defaults are kept small so the first run feels responsive.
""")
    st.warning("Educational tool only — not investment advice. Backtested performance does not "
               "guarantee future results. Small-sample ML/RL models are especially prone to overfitting.")
