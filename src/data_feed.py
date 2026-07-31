"""
Live + historical market data feed.

Primary source: yfinance (free, no API key, scrapes Yahoo Finance).
Fallback source: Alpha Vantage (needs a free key from alphavantage.co) —
used automatically if yfinance fails/rate-limits, or if the user forces it.

Everything is wrapped in short-TTL caches so the dashboard can be left running
and will pull fresh data on its own rather than showing a frozen snapshot.
"""
from __future__ import annotations

import os
import time
import requests
import pandas as pd
import streamlit as st
import yfinance as yf

ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"


def _get_av_key() -> str | None:
    return st.session_state.get("av_api_key") or os.environ.get("ALPHAVANTAGE_API_KEY")


@st.cache_data(ttl=60, show_spinner=False)
def get_history_yf(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """Historical OHLCV via yfinance. TTL=60s so 'live' views actually refresh."""
    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        multi_level_index=False,
    )
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.rename(columns=str.title)
    df.index.name = "Date"
    return df


@st.cache_data(ttl=300, show_spinner=False)
def get_history_alpha_vantage(ticker: str, api_key: str, adjusted: bool = True) -> pd.DataFrame:
    """Historical daily OHLCV via Alpha Vantage (fallback source)."""
    function = "TIME_SERIES_DAILY_ADJUSTED" if adjusted else "TIME_SERIES_DAILY"
    params = {
        "function": function,
        "symbol": ticker,
        "outputsize": "full",
        "apikey": api_key,
    }
    r = requests.get(ALPHA_VANTAGE_BASE, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    key = [k for k in data.keys() if "Time Series" in k]
    if not key:
        return pd.DataFrame()
    series = data[key[0]]
    df = pd.DataFrame(series).T
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"
    df = df.sort_index()
    rename = {
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. adjusted close": "Adj Close",
        "6. volume": "Volume",
        "5. volume": "Volume",
    }
    df = df.rename(columns=rename)
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if "Adj Close" in df.columns:
        df["Close"] = df["Adj Close"]
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    return df[keep]


def get_history(ticker: str, period: str = "2y", interval: str = "1d", prefer: str = "yfinance") -> tuple[pd.DataFrame, str]:
    """
    Try the preferred source first, fall back automatically. Returns (df, source_used).
    """
    order = ["yfinance", "alpha_vantage"] if prefer == "yfinance" else ["alpha_vantage", "yfinance"]
    last_err = None
    for source in order:
        try:
            if source == "yfinance":
                df = get_history_yf(ticker, period=period, interval=interval)
                if not df.empty:
                    return df, "yfinance"
            else:
                key = _get_av_key()
                if key:
                    df = get_history_alpha_vantage(ticker, key)
                    if not df.empty:
                        return df, "alpha_vantage"
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    if last_err:
        raise RuntimeError(f"All data sources failed for {ticker}: {last_err}")
    return pd.DataFrame(), "none"


@st.cache_data(ttl=5, show_spinner=False)
def get_live_quote(ticker: str) -> dict:
    """Fast, low-latency-ish quote for the 'Live Market' view (5s cache).

    5s is close to the practical floor for yfinance: Yahoo's own quote feed
    doesn't tick faster than that for most symbols, and polling much harder
    risks IP-level rate-limiting since this hits an unofficial endpoint.
    """
    try:
        t = yf.Ticker(ticker)
        fi = t.fast_info
        price = fi.get("last_price") or fi.get("lastPrice")
        prev_close = fi.get("previous_close") or fi.get("previousClose")
        change = None
        change_pct = None
        if price is not None and prev_close:
            change = price - prev_close
            change_pct = (change / prev_close) * 100
        return {
            "ticker": ticker,
            "price": price,
            "prev_close": prev_close,
            "change": change,
            "change_pct": change_pct,
            "day_high": fi.get("day_high") or fi.get("dayHigh"),
            "day_low": fi.get("day_low") or fi.get("dayLow"),
            "volume": fi.get("last_volume") or fi.get("lastVolume"),
            "market_cap": fi.get("market_cap") or fi.get("marketCap"),
            "as_of": pd.Timestamp.now(),
            "ok": price is not None,
        }
    except Exception as e:  # noqa: BLE001
        # Keep the same schema as the success path — a partial-failure batch (some
        # tickers rate-limited, others fine) must not leave columns like "price"
        # missing from the resulting DataFrame entirely.
        return {
            "ticker": ticker, "price": None, "prev_close": None, "change": None,
            "change_pct": None, "day_high": None, "day_low": None, "volume": None,
            "market_cap": None, "as_of": pd.Timestamp.now(), "ok": False, "error": str(e),
        }


def get_live_quotes(tickers: list[str]) -> pd.DataFrame:
    rows = [get_live_quote(t) for t in tickers]
    return pd.DataFrame(rows)
