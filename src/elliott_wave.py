"""
Elliott Wave pivot/wave/target engine.

Ported from a hand-built Elliott Wave Tracker artifact (ZigZag pivot detection,
impulse/correction rule classification, Fibonacci target cascades, and a
walk-forward accuracy backtest). The original ran on an embedded price
snapshot fetched once via an MCP connector, with only the actively-viewed
ticker ever refreshed live (a workaround for that platform's per-page
subscription cap). Here every ticker is fetched live through this app's own
data feed (src/data_feed.py) instead — no connector, no embedded snapshot,
no single-ticker-only restriction.

All functions operate on a plain `series`: a list of
{"date": "YYYY-MM-DD", "close": float, "high": float, "low": float} dicts,
oldest first. Convert a data_feed OHLC DataFrame with `series_from_df`.
"""
from __future__ import annotations

RETR_RATIOS = [0.382, 0.5, 0.618, 0.786]
EXT_RATIOS = [1.0, 1.272, 1.618, 2.618]
RATIO_ORDER = RETR_RATIOS + EXT_RATIOS
RATIO_LABEL = {
    0.382: ".382", 0.5: ".5", 0.618: ".618", 0.786: ".786",
    1.0: "1.0", 1.272: "1.272", 1.618: "1.618", 2.618: "2.618",
}

MIN_CONF = 30
BT_THRESHOLD_PCT = 3.0  # uniform across the whole scanned universe, on purpose — not tuned per name
DEFAULT_THRESHOLD_PCT = 3.0
TS_RELIABILITY_MIN_N = 20


def series_from_df(df) -> list[dict]:
    """OHLC DataFrame (DatetimeIndex, High/Low/Close columns) -> our series-of-dicts shape."""
    out = []
    for ts, row in df.iterrows():
        out.append({
            "date": ts.strftime("%Y-%m-%d"),
            "close": float(row["Close"]), "high": float(row["High"]), "low": float(row["Low"]),
        })
    return out


# ============================================================
# a. ZigZag pivot detector — sourced from real bar HIGH/LOW (standard swing-pivot
# practice), not close-only. Each pivot also records confirm_idx: the bar index at
# which its reversal past threshold first became detectable. Nothing about a
# pivot's finalized price/idx/confirm_idx ever depends on bars after confirm_idx —
# that's what makes the walk-forward backtest below lookahead-free by construction.
# ============================================================
def zigzag(series: list[dict], pct_threshold: float) -> list[dict]:
    if len(series) < 2:
        return []
    pivots = [{"idx": 0, "date": series[0]["date"], "price": series[0]["close"], "type": None, "confirm_idx": 0}]
    direction = 0  # 0=unset, 1=tracking a HIGH candidate, -1=tracking a LOW candidate
    cand_price = series[0]["close"]

    for i in range(1, len(series)):
        hi, lo = series[i]["high"], series[i]["low"]
        confirmed_high = confirmed_low = False

        if direction != -1:
            drop_pct = (cand_price - lo) / cand_price * 100
            if drop_pct >= pct_threshold:
                pivots[-1]["type"] = "high"
                pivots[-1]["confirm_idx"] = i
                direction = -1
                cand_price = lo
                pivots.append({"idx": i, "date": series[i]["date"], "price": lo, "type": None, "confirm_idx": None})
                confirmed_high = True
        if not confirmed_high and direction != 1:
            rise_pct = (hi - cand_price) / cand_price * 100
            if rise_pct >= pct_threshold:
                pivots[-1]["type"] = "low"
                pivots[-1]["confirm_idx"] = i
                direction = 1
                cand_price = hi
                pivots.append({"idx": i, "date": series[i]["date"], "price": hi, "type": None, "confirm_idx": None})
                confirmed_low = True
        if confirmed_high or confirmed_low:
            continue

        if direction == 1 and hi > cand_price:
            cand_price = hi
            pivots[-1].update(price=hi, date=series[i]["date"], idx=i)
        elif direction == -1 and lo < cand_price:
            cand_price = lo
            pivots[-1].update(price=lo, date=series[i]["date"], idx=i)
        elif direction == 0:
            if hi > cand_price:
                cand_price = hi
                pivots[-1].update(price=hi, date=series[i]["date"], idx=i)
            elif lo < cand_price:
                cand_price = lo
                pivots[-1].update(price=lo, date=series[i]["date"], idx=i)

    if len(pivots) > 1:
        last_p, prev_p = pivots[-1], pivots[-2]
        if last_p["type"] is None:  # still forming — confirm_idx stays None (no lookahead)
            last_p["type"] = "high" if last_p["price"] > prev_p["price"] else "low"
        if pivots[0]["type"] is None:
            pivots[0]["type"] = "low" if pivots[1]["price"] > pivots[0]["price"] else "high"
    return pivots


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def closeness_to(ratio: float, targets: list[float]) -> float:
    d = min(abs(ratio - t) for t in targets)
    return clamp01(1 - d / 0.5)


# ============================================================
# b. EW rule classifiers — impulse (5-pivot run) and correction (3-pivot A-B-C) fits,
# with a confidence score built from Fibonacci-ratio closeness + rule compliance.
# ============================================================
def classify_impulse_window(pivots: list[dict], start_idx: int) -> dict | None:
    if start_idx + 5 >= len(pivots):
        return None
    P = [pivots[start_idx + k] for k in range(6)]
    direction = 1 if P[1]["price"] > P[0]["price"] else -1

    def leg(i):
        return (P[i]["price"] - P[i - 1]["price"]) * direction

    w1, w3, w5 = leg(1), leg(3), leg(5)
    wave2_no_full_retrace = (P[2]["price"] > P[0]["price"]) if direction > 0 else (P[2]["price"] < P[0]["price"])
    wave3_not_shortest = not (abs(w3) < abs(w1) and abs(w3) < abs(w5))
    overlap = (P[4]["price"] < P[1]["price"]) if direction > 0 else (P[4]["price"] > P[1]["price"])
    is_diagonal = overlap
    retr2 = abs(leg(2)) / abs(w1 or 1e-9)
    retr4 = abs(leg(4)) / abs(w3 or 1e-9)
    ext5 = abs(w5) / abs(w1 or 1e-9)
    c2 = closeness_to(retr2, [0.382, 0.5, 0.618, 0.786])
    c4 = closeness_to(retr4, [0.236, 0.382, 0.5])
    c5 = closeness_to(ext5, [0.618, 1.0, 1.618])
    confidence = (c2 * 0.30 + c4 * 0.25 + c5 * 0.15 + (0.20 if wave3_not_shortest else 0)
                  + (0.10 if wave2_no_full_retrace else 0)) * 100
    if is_diagonal:
        confidence *= 0.85
    confidence = round(clamp01(confidence / 100) * 100)
    valid = wave2_no_full_retrace and wave3_not_shortest and (not overlap or is_diagonal)
    return {
        "kind": "impulse", "dir": direction, "pivots": P, "is_diagonal": is_diagonal,
        "confidence": confidence, "valid": valid,
        "rules": {"wave2_no_full_retrace": wave2_no_full_retrace, "wave3_not_shortest": wave3_not_shortest,
                  "no_overlap": not overlap},
        "ratios": {"retr2": round(retr2, 3), "retr4": round(retr4, 3), "ext5": round(ext5, 3)},
    }


def classify_correction_window(pivots: list[dict], start_idx: int) -> dict | None:
    if start_idx + 3 >= len(pivots):
        return None
    P = [pivots[start_idx + k] for k in range(4)]
    len_a = abs(P[1]["price"] - P[0]["price"])
    len_b = abs(P[2]["price"] - P[1]["price"])
    retr_b = len_b / (len_a or 1e-9)
    b_ok = 0.382 <= retr_b <= 0.786
    closeness = clamp01(1 - min(abs(retr_b - 0.5), abs(retr_b - 0.618)) / 0.4)
    confidence = round(closeness * 70 + (30 if b_ok else 0))
    return {"kind": "correction", "pivots": P, "retr_b": round(retr_b, 3), "b_ok": b_ok, "confidence": confidence}


def scan_waves(pivots: list[dict]) -> dict:
    """Scan every window, greedily choose the highest-confidence non-overlapping chain."""
    fits = []
    for i in range(len(pivots)):
        imp = classify_impulse_window(pivots, i)
        if imp:
            fits.append({**imp, "start": i, "end": i + 5})
        corr = classify_correction_window(pivots, i)
        if corr:
            fits.append({**corr, "start": i, "end": i + 3})
    fits.sort(key=lambda f: -f["confidence"])
    chosen, used = [], set()
    for f in fits:
        if not any(i in used for i in range(f["start"] + 1, f["end"])):
            chosen.append(f)
            used.update(range(f["start"] + 1, f["end"]))
    chosen.sort(key=lambda f: f["start"])
    return {"fits": fits, "chosen": chosen}


def nested_fit(full_series: list[dict], leg_start_idx: int, leg_end_idx: int, sub_threshold_pct: float) -> dict | None:
    """Recurse one level: reclassify a chosen leg's own index range at a finer threshold."""
    sub = full_series[leg_start_idx:leg_end_idx + 1]
    if len(sub) < 4:
        return None
    sub_pivots = zigzag(sub, sub_threshold_pct)
    for p in sub_pivots:
        p["idx"] += leg_start_idx
    fit = None
    if len(sub_pivots) >= 6:
        fit = classify_impulse_window(sub_pivots, 0)
    if not fit and len(sub_pivots) >= 4:
        fit = classify_correction_window(sub_pivots, 0)
    if fit:
        fit["sub_pivots"] = sub_pivots
    return fit


# ============================================================
# c. Fibonacci target cascade at pivot p_i (defaults to the last pivot): retracement
# levels measure back from p_i by the just-completed leg (p_{i-1} -> p_i); extension
# levels project forward from p_i using the prior leg's length (p_{i-2} -> p_{i-1}),
# in that leg's own direction. Used both for the live "current cascade" panel and by
# the walk-forward backtest below — same function, called at different points in history.
# ============================================================
def fib_cascade(pivots: list[dict], idx: int | None = None) -> list[dict]:
    idx = len(pivots) - 1 if idx is None else idx
    if idx < 2 or idx >= len(pivots):
        return []
    pi, p1, p0 = pivots[idx], pivots[idx - 1], pivots[idx - 2]
    just_leg = pi["price"] - p1["price"]
    prior_leg = p1["price"] - p0["price"]
    cascade = []
    for r in RETR_RATIOS:
        cascade.append({"kind": "retracement", "ratio": r, "price": round(pi["price"] - just_leg * r, 2),
                         "wave_tag": "corrective pullback zone (wave 2 / B)"})
    for r in EXT_RATIOS:
        cascade.append({"kind": "extension", "ratio": r, "price": round(pi["price"] + prior_leg * r, 2),
                         "wave_tag": "impulsive projection (wave 3 / 5 / C)"})
    cascade.sort(key=lambda c: c["price"])
    return cascade


# ============================================================
# d. Basket agreement — % of a correlated basket sharing the leader's current phase.
# ============================================================
def classify_phase(series: list[dict], threshold: float) -> str:
    piv = zigzag(series, threshold)
    if len(piv) < 3:
        return "unknown"
    last_dir = 1 if piv[-1]["price"] > piv[-2]["price"] else -1
    overall_dir = 1 if piv[-1]["price"] > piv[0]["price"] else -1
    return "bullish-impulse" if last_dir == overall_dir else "bearish-correction"


def basket_agreement(leader_key: str, basket_tickers: list[str], series_by_ticker: dict[str, list[dict]],
                      threshold_by_ticker: dict[str, float] | None = None) -> dict:
    threshold_by_ticker = threshold_by_ticker or {}
    if leader_key not in series_by_ticker:
        return {"leader_phase": "unknown", "matched": 0, "total": 0, "pct": 0, "scored": []}
    leader_phase = classify_phase(series_by_ticker[leader_key], threshold_by_ticker.get(leader_key, DEFAULT_THRESHOLD_PCT))
    scored, matched, total = [], 0, 0
    for k in basket_tickers:
        if k == leader_key or k not in series_by_ticker:
            continue
        phase = classify_phase(series_by_ticker[k], threshold_by_ticker.get(k, DEFAULT_THRESHOLD_PCT))
        is_match = phase == leader_phase
        matched += int(is_match)
        total += 1
        scored.append({"ticker": k, "phase": phase, "is_match": is_match})
    return {"leader_phase": leader_phase, "matched": matched, "total": total,
            "pct": round(matched / total * 100) if total else 0, "scored": scored}


# ============================================================
# 2b. Walk-forward Fibonacci-target backtest ("Model Accuracy").
#
# For every pivot p_i (i>=2) with a resolved confirm_idx (the still-forming trailing
# pivot is excluded — testing it would BE lookahead):
#   1. Generate its Fibonacci cascade via fib_cascade(pivots, i) — the exact same
#      function the live panel uses — using only pivots p_0..p_i.
#   2. Open a forward test window of W trading days starting the bar AFTER confirm_idx.
#   3. For each target level, check whether any bar's [low,high] range intersects the
#      target's +/-tolerance band inside that window. Record hit/miss and days-to-hit.
#   4. Confidence = closeness of |just-completed leg| / |prior leg| to the nearest
#      canonical ratio in RATIO_ORDER (0-100).
# A pivot whose full W-day forward window would run past the end of available history
# is skipped entirely — a partial window would understate hit-rate for no principled
# reason. This means the most recent few pivots are never scored.
# ============================================================
def backtest_ticker(ticker: str, series: list[dict], window: int = 20, tolerance: float = 0.5) -> list[dict]:
    if len(series) < 10:
        return []
    pivots = zigzag(series, BT_THRESHOLD_PCT)
    records = []
    for i in range(2, len(pivots)):
        pi = pivots[i]
        if pi["confirm_idx"] is None:
            continue
        p1, p0 = pivots[i - 1], pivots[i - 2]
        just_leg, prior_leg = pi["price"] - p1["price"], p1["price"] - p0["price"]
        if not just_leg or not prior_leg:
            continue
        leg_ratio = abs(just_leg) / abs(prior_leg)
        confidence = round(closeness_to(leg_ratio, RATIO_ORDER) * 100)
        window_start = pi["confirm_idx"] + 1
        window_end = window_start + window - 1
        if window_start >= len(series) or window_end > len(series) - 1:
            continue
        for tg in fib_cascade(pivots, i):
            hit, days_to_hit = False, None
            tol_abs = abs(tg["price"]) * (tolerance / 100)
            for b in range(window_start, window_end + 1):
                if series[b]["high"] >= tg["price"] - tol_abs and series[b]["low"] <= tg["price"] + tol_abs:
                    hit, days_to_hit = True, b - window_start + 1
                    break
            records.append({"ticker": ticker, "pivot_idx": i, "ratio": tg["ratio"], "kind": tg["kind"],
                             "hit": hit, "days_to_hit": days_to_hit, "confidence": confidence})
    return records


def aggregate_backtest(records: list[dict]) -> dict:
    """Overall hit-rate (with N), by ratio bucket, by confidence quartile (cut points
    computed FRESH from this exact record set), mean/median days-to-hit among hits."""
    n = len(records)
    hits = sum(1 for r in records if r["hit"])

    by_ratio = {r: {"n": 0, "hits": 0, "kind": "retracement" if r in RETR_RATIOS else "extension"} for r in RATIO_ORDER}
    for rec in records:
        by_ratio[rec["ratio"]]["n"] += 1
        if rec["hit"]:
            by_ratio[rec["ratio"]]["hits"] += 1

    conf_sorted = sorted(r["confidence"] for r in records)

    def pctile(p):
        if not conf_sorted:
            return 0
        return conf_sorted[min(len(conf_sorted) - 1, int(p * len(conf_sorted)))]

    q1c, q2c, q3c = pctile(0.25), pctile(0.5), pctile(0.75)

    def quartile_of(c):
        if c <= q1c:
            return 0
        if c <= q2c:
            return 1
        if c <= q3c:
            return 2
        return 3

    q_ranges = [(conf_sorted[0] if conf_sorted else 0, q1c), (q1c, q2c), (q2c, q3c),
                (q3c, conf_sorted[-1] if conf_sorted else 0)]
    by_quartile = [{"label": lbl, "n": 0, "hits": 0, "range": q_ranges[i]}
                   for i, lbl in enumerate(["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"])]
    for r in records:
        qi = quartile_of(r["confidence"])
        by_quartile[qi]["n"] += 1
        if r["hit"]:
            by_quartile[qi]["hits"] += 1

    hit_days = sorted(r["days_to_hit"] for r in records if r["hit"] and r["days_to_hit"] is not None)
    mean_days = (sum(hit_days) / len(hit_days)) if hit_days else None
    median_days = None
    if hit_days:
        mid = len(hit_days) // 2
        median_days = hit_days[mid] if len(hit_days) % 2 else (hit_days[mid - 1] + hit_days[mid]) / 2

    pivots_tested = {(r["ticker"], r["pivot_idx"]) for r in records}
    return {"n": n, "hits": hits, "rate": (hits / n) if n else None, "by_ratio": by_ratio,
            "by_quartile": by_quartile, "mean_days": mean_days, "median_days": median_days,
            "pivot_count": len(pivots_tested)}


# ============================================================
# 3. Per-ticker compute — active-threshold fit, one finer nested sub-fit, and one
# coarser outer fit (for a 3-degree wave tree: Primary / Intermediate / Minor).
# ============================================================
def compute_for_ticker(ticker: str, series: list[dict], threshold: float) -> dict:
    pivots = zigzag(series, threshold)
    scan = scan_waves(pivots)
    display_fits = [f for f in scan["chosen"] if f["confidence"] >= MIN_CONF]
    cascade = fib_cascade(pivots) if len(pivots) >= 3 else []
    current_fit = display_fits[-1] if display_fits else None
    nested = None
    if current_fit:
        leg_start_idx = pivots[current_fit["start"]]["idx"]
        leg_end_idx = pivots[current_fit["end"]]["idx"]
        if leg_end_idx - leg_start_idx >= 4:
            nested = nested_fit(series, leg_start_idx, leg_end_idx, max(0.8, threshold / 2.5))
    outer_pivots = zigzag(series, threshold * 2.5)
    outer_scan = scan_waves(outer_pivots)
    outer_fits = [f for f in outer_scan["chosen"] if f["confidence"] >= MIN_CONF]
    outer_fit = outer_fits[-1] if outer_fits else None
    return {"ticker": ticker, "series": series, "pivots": pivots, "scan": scan, "display_fits": display_fits,
            "cascade": cascade, "current_fit": current_fit, "nested": nested, "outer_fit": outer_fit}


# ============================================================
# 2c. Top Setups — composite opportunity screener. A pure aggregation/ranking layer
# over compute_for_ticker / fib_cascade / backtest_ticker — no new price-forecasting
# logic here, only a scoring layer on top of what's already computed.
# ============================================================
def _nearest_support(cascade, last_close):
    best = None
    for c in cascade:
        if c["kind"] == "retracement" and c["price"] <= last_close and (best is None or c["price"] > best["price"]):
            best = c
    return best


def _nearest_upside(cascade, last_close):
    best = None
    for c in cascade:
        if c["kind"] == "extension" and c["price"] > last_close and (best is None or c["price"] < best["price"]):
            best = c
    return best


def _invalidation_level(current_fit, pivots, nearest_support):
    if current_fit and current_fit["kind"] == "impulse":
        return pivots[current_fit["start"]]["price"]
    if current_fit and current_fit["kind"] == "correction":
        a_start, a_end = current_fit["pivots"][0], current_fit["pivots"][1]
        a_leg = a_end["price"] - a_start["price"]
        return round(a_end["price"] - a_leg * 0.786, 2)
    return nearest_support["price"] if nearest_support else None


def compute_top_setups(universe: list[str], series_by_ticker: dict[str, list[dict]],
                        sector_by_ticker: dict[str, str] | None = None,
                        threshold_by_ticker: dict[str, float] | None = None,
                        bt_window: int = 20, bt_tolerance: float = 0.5) -> list[dict]:
    sector_by_ticker = sector_by_ticker or {}
    threshold_by_ticker = threshold_by_ticker or {}

    all_records, by_ticker = [], {}
    for tk in universe:
        series = series_by_ticker.get(tk)
        if not series:
            continue
        recs = backtest_ticker(tk, series, bt_window, bt_tolerance)
        by_ticker[tk] = recs
        all_records.extend(recs)

    pooled_by_ratio = {r: {"n": 0, "hits": 0} for r in RATIO_ORDER}
    for rec in all_records:
        pooled_by_ratio[rec["ratio"]]["n"] += 1
        if rec["hit"]:
            pooled_by_ratio[rec["ratio"]]["hits"] += 1

    rows = []
    for tk in universe:
        series = series_by_ticker.get(tk)
        if not series:
            continue
        threshold = threshold_by_ticker.get(tk, DEFAULT_THRESHOLD_PCT)
        data = compute_for_ticker(tk, series, threshold)
        pivots, current_fit, cascade = data["pivots"], data["current_fit"], data["cascade"]
        last_close = series[-1]["close"]

        nearest_support = _nearest_support(cascade, last_close)
        nearest_upside = _nearest_upside(cascade, last_close)

        entry_proximity_pct = (abs(last_close - nearest_support["price"]) / last_close * 100) if nearest_support else None
        entry_score = 0.0 if entry_proximity_pct is None else clamp01(1 - entry_proximity_pct / 5) * 100
        upside_pct = (nearest_upside["price"] - last_close) / last_close * 100 if nearest_upside else 0.0

        invalidation = _invalidation_level(current_fit, pivots, nearest_support)
        downside_pct = (abs(last_close - invalidation) / last_close * 100) if invalidation is not None else None
        risk_reward = (upside_pct / downside_pct) if (downside_pct and downside_pct > 0) else ((upside_pct / 0.5) if upside_pct > 0 else 0.0)

        confidence = current_fit["confidence"] if current_fit else 50

        target_ratio = nearest_upside["ratio"] if nearest_upside else (nearest_support["ratio"] if nearest_support else None)
        ticker_records = by_ticker.get(tk, [])
        if ticker_records:
            ratio_recs = [r for r in ticker_records if target_ratio is not None and r["ratio"] == target_ratio]
            if target_ratio is not None and len(ratio_recs) >= TS_RELIABILITY_MIN_N:
                hr_n = len(ratio_recs)
                historical_reliability = sum(1 for r in ratio_recs if r["hit"]) / hr_n * 100
                hr_tier, hr_detail = "ratio-specific", (
                    f"Ratio-specific: this ticker's own backtest records for ratio {RATIO_LABEL[target_ratio]} "
                    f"(N={hr_n} ≥ {TS_RELIABILITY_MIN_N}).")
            else:
                hr_n = len(ticker_records)
                historical_reliability = sum(1 for r in ticker_records if r["hit"]) / hr_n * 100
                hr_tier = "ticker-overall"
                hr_detail = (
                    f"Ticker-overall fallback: ratio {RATIO_LABEL[target_ratio]} sample for this ticker was only "
                    f"N={len(ratio_recs)} (< {TS_RELIABILITY_MIN_N}), so this ticker's all-ratio hit-rate (N={hr_n}) is used instead."
                ) if target_ratio is not None else (
                    f"Ticker-overall fallback: no nearby support/target level to match a specific ratio, so this "
                    f"ticker's all-ratio hit-rate (N={hr_n}) is used instead.")
        elif target_ratio is not None:
            pooled = pooled_by_ratio[target_ratio]
            hr_n = pooled["n"]
            historical_reliability = (pooled["hits"] / pooled["n"] * 100) if pooled["n"] else 50
            hr_tier = "pooled all-universe"
            hr_detail = (f"Pooled all-universe fallback: this ticker has no backtest records at all, so the pooled "
                          f"hit-rate for ratio {RATIO_LABEL[target_ratio]} across every scanned ticker (N={hr_n}) is used instead.")
        else:
            hr_n = 0
            historical_reliability = 50
            hr_tier = "neutral default"
            hr_detail = ("Neutral default: this ticker has no backtest records and no nearby support/target level "
                          "to match a ratio against, so a neutral 50% is used.")

        score = (0.30 * entry_score + 0.25 * clamp01(risk_reward / 3) * 100 + 0.20 * confidence
                 + 0.15 * historical_reliability + 0.10 * clamp01(upside_pct / 10) * 100)

        rows.append({
            "ticker": tk, "sector": sector_by_ticker.get(tk, ""), "phase": classify_phase(series, threshold),
            "last_close": last_close, "nearest_support": nearest_support, "nearest_upside": nearest_upside,
            "entry_proximity_pct": entry_proximity_pct, "entry_score": entry_score,
            "upside_pct": upside_pct, "invalidation": invalidation, "downside_pct": downside_pct,
            "risk_reward": risk_reward, "confidence": confidence,
            "historical_reliability": historical_reliability, "hr_n": hr_n, "hr_tier": hr_tier, "hr_detail": hr_detail,
            "score": score,
        })

    rows.sort(key=lambda r: -r["score"])
    return rows
