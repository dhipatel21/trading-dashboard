"""
Static content for the Elliott Wave tab — reproduced from the original Elliott Wave
Tracker artifact: the family group chat's self-reported call log, the playbook
distilled from that chat, and the methodology/caveats write-ups. The methodology
and caveats text is lightly adapted in the two places that described the original's
MCP-connector-based live feed / embedded snapshot, which don't apply to this port
(every ticker here can fetch live via this app's own data feed — no connector, no
embedded snapshot, no single-ticker-only restriction). Everything else is verbatim.
"""

PINNED_TICKERS = ["QQQ", "MU", "AAOI", "NVDA", "CRWD", "ARM", "AEHR"]
BASKET_TICKERS = PINNED_TICKERS
BASKET_LEADER = "QQQ"
PROXY_LABEL = {"QQQ": "QQQ (NDX proxy)", "SPY": "SPY (SPX proxy)"}

# date, ticker, wave, target, timeframe, outcome, resolution ('hit' | 'revised' | 'excluded')
CALL_LOG = [
    ("Mon 7/20 4:48am", "NDX", "i of C bottom", "28220", "Fri (prior)", "confirmed complete", "hit"),
    ("Mon 7/20 4:48am", "NDX", "ii of C bounce top", "29200", 'by "tomorrow"', "superseded, see below", "revised"),
    ("Mon 7/20 4:48am", "NDX", "iii of C down", "~27500", "after ii top", "on path, later refined", "revised"),
    ("Mon 7/20 4:48am", "NDX", "iv/v of C bottom", "27000", "by 7/31", "superseded to 27400 then 26800-27000", "revised"),
    ("Mon 7/20 4:48am", "NDX", "wave 3 rally target", "32000", "late Sept", "still standing (long-range)", "excluded"),
    ("Mon 7/20 4:48am", "MU", "near-term top", "940-960", "this week", "roughly hit (MU topped ~1000-1010 by 7/23)", "hit"),
    ("Mon 7/20 4:48am", "MU", "bottom", "700-750", "by 7/31", "hit: MU tagged the 700 target (noted 7/30)", "hit"),
    ("Mon 7/20 4:48am", "MU", "rally target", "1400", "late Sept", "revised later to 1500", "revised"),
    ("Mon 7/20, later", "NDX", "wave II of C top (.618)", "29225", "—", "topped slightly under, ~29500 area cited next day", "revised"),
    ("Mon 7/20", "NDX", "(iii)(iv)(v) of c of ii ladder", "29300, 29000, 29500", "Wed/Thu", "roughly played out (topping process took to 7/22-23)", "hit"),
    ("Tue 7/21 5:14am", "MU", "top", "1000", "today/tomorrow/this wk", "hit: MU topped overnight at 1000 (confirmed 7/23)", "hit"),
    ("Tue 7/21 5:14am", "MU", "bottom", "750-800", "by 7/31-8/7", "in progress, revised path continues", "excluded"),
    ("Tue 7/21 5:14am", "NDX", "top", "29500", "this week", "roughly hit", "hit"),
    ("Tue 7/21 5:14am", "NDX", "bottom", "27500-28000", "by 7/31-8/7", "revised lower (27400, then 27200-27400, then 26800-27000)", "revised"),
    ("Tue 7/21 5:14am", "AAOI", "top", "120-125", "—", "hit: AAOI topped Tuesday per 7/23 text", "hit"),
    ("Tue 7/21 5:14am", "AAOI", "bottom", "90-100", "—", "pending", "excluded"),
    ("Tue 7/21 5:14am", "AAOI", "rally target", "400-450", "7-12 months", "standing", "excluded"),
    ("Tue 7/21 5:14am", "MU", "rally target (post-dump)", "1500", "—", "standing, reaffirmed 7/24 & 7/27", "excluded"),
    ("Tue 7/21 7:29am", "CRWD", "target", "~170", "by early Aug", "not otherwise confirmed in text", "excluded"),
    ("Wed 7/22 5:14am", "NDX", "final top", "~29300", "—", "roughly matches", "hit"),
    ("Wed 7/22 5:14am", "MU", "final top", "1000", "—", "hit", "hit"),
    ("Wed 7/22 5:14am", "NDX", "dump target", "27400", "by 7/31 or early Aug", "revised path, eventually target became 26800-27000", "revised"),
    ("Wed 7/22 5:14am", "MU", "dump target", "750-800", "by 7/31 or early Aug", "in progress", "excluded"),
    ("Wed 7/22 5:14am", "AAOI", "top then bottom", "122-130 then 90-100", "—", "AAOI topped ~Tue per later text", "hit"),
    ("Thu 7/23 5:37am", "MU", "topped", "1000 (confirmed)", "overnight", "CONFIRMED HIT", "hit"),
    ("Thu 7/23 5:37am", "NDX", "topped", "Tuesday (confirmed)", "—", "CONFIRMED", "hit"),
    ("Thu 7/23 5:37am", "AAOI", "topped", "Tuesday (confirmed)", "—", "CONFIRMED", "hit"),
    ("Thu 7/23 10:03am", "NDX", "guess", "28700-28750", "by tomorrow", "roughly hit (28606-28800 area reached)", "hit"),
    ("Thu 7/23 10:03am", "MU", "guess", "1020-1050", "by tomorrow", "MU 1010-1030 area, close", "hit"),
    ("Thu 7/23 12:12pm", "MU", "ED 5th wave (abc)", "1015,1000,1025-1030", "intraday", "choppy, roughly in range", "hit"),
    ("Fri 7/24 4:57am", "NDX", "3-wave move up", "28700", "by close or Mon AM", "roughly hit", "hit"),
    ("Fri 7/24 4:57am", "MU", "intraday path", "1010-1015, then 995-1000, then 1025", "by 10:30am", "MU tagged 700 target later confirms downside eventually won out", "revised"),
    ("Fri 7/24 4:57am", "MU", "bottom", "750-800", "next 7-14 days", "superseded — MU tagged 700 (better than target) by 7/30", "revised"),
    ("Fri 7/24 4:57am", "MU", "post-bottom rally", "1500+", "next 6-8 months", "standing", "excluded"),
    ("Fri 7/24 6:53am", "NDX", '"we headed down"', "—", "—", 'CONFIRMED (contact replied "Damn")', "hit"),
    ("Fri 7/24 11:26am", "NDX", "bottom precondition", "27400 (must hit before any bottom call)", "by 7/31 or into Aug", "superseded, actual low undercut to ~27258 by 7/30", "revised"),
    ("Mon 7/27 4:46am", "NDX", "wave b of v top", "28800", "today/tomorrow", "roughly hit", "hit"),
    ("Mon 7/27 4:46am", "NDX", "(a) of b of v", "28606 (premarket, already tagged)", "—", "CONFIRMED", "hit"),
    ("Mon 7/27 4:46am", "NDX", "(b) of b of v", "28270", "this morning", "pending/roughly on path", "excluded"),
    ("Mon 7/27 4:46am", "NDX", "(c) of b of v top", "28800", "by Tuesday", "roughly hit", "hit"),
    ("Mon 7/27 4:46am", "NDX", "bottom", "27500-27600", "by Friday", "revised slightly (actual low ~27258-27736 area by 7/29-30)", "revised"),
    ("Mon 7/27 4:46am", "NDX", "massive rally target", "32000", "late Sept, as diagonal", "standing (long-range)", "excluded"),
    ("Mon 7/27 4:46am", "MU", "bottom", "750-800", "by Friday", "MU beat this, tagged 700 by 7/30", "hit"),
    ("Mon 7/27 4:46am", "MU", "post-bottom targets", "1300, 1400, 1500", "next 2 months", "standing", "excluded"),
    ("Mon 7/27 6:25am", "NDX", "ED wave v of C bottom", "below 28000, ideally 27400-27600", "by end of this/next wk", "actual low undercut target (~27258 by 7/30)", "revised"),
    ("Mon 7/27 8:37am", "NDX", "guess path (i)(ii)(iii)", "27750, 28250, 27350", "—", 'starting point, "currently at 27962"', "excluded"),
    ("Mon 7/27 8:37am", "NDX", "afternoon drop", "~200 pts lower", "that afternoon", "roughly on path", "hit"),
    ("Mon 7/27 1:27pm", "NDX", "bite-of-apple top", "28600", "by Wed", "revised down from earlier 28800", "revised"),
    ("Mon 7/27 1:27pm", "MU", "bite-of-apple top", "950", "by Wed", "in range of actual (937-980 area)", "hit"),
    ("Mon 7/27 1:27pm", "NDX", "final leg bottom", "27200-27400", "over next 7 days", "actual low ~27258, essentially CONFIRMED HIT", "hit"),
    ("Mon 7/27 1:27pm", "MU", "final leg bottom", "750-800", "over next 7 days", "MU beat this, tagged 700 (better/lower than target)", "hit"),
    ('"Yesterday" 5:56pm (~7/29)', "NDX", "bounce target", "29300-29500", "by 8/7-8/10", "forward-looking, not yet resolved", "excluded"),
    ('"Yesterday" 5:56pm (~7/29)', "NDX", "next leg down", "one more fast leg down", "late Aug, before NVDA earnings 8/24", "forward-looking", "excluded"),
    ("Today 7/30 9:44am", "MU", "today/tomorrow path", "880, then 760, then 960 by 8/10", "—", "forward-looking; MU already tagged 700 (better than the 750-800 target)", "excluded"),
    ("Today 7/30 9:44am", "NDX", '"getting very very micro" (quoted from "yesterday" 11:38am text)', "27270, 27800, 26800-27000 by Friday close", "—",
     'CONFIRMED HIT — Dad notes it "played out exactly... did it all in 4.5 hours... didn\'t even take til Friday"', "hit"),
    ("Today 7/30 11:47am", "SPX", "two scenarios on chart", 'pullback to yellow "alt 2" (bullish case) OR pullback to white "iii" (bearish case)',
     "tomorrow", "forward-looking / unresolved fork", "excluded"),
    ("Today 7/30 2:45pm", "NDX/basket", '"bottomed yesterday, reversed today with first five up"', "—", "now expect large rally",
     'forward-looking, latest view as of "today"', "excluded"),
]

PLAYBOOK = [
    (1, "Fractal / nested wave counting",
     'Tracks ~5 degrees at once: Grand letters (A,B,C) > Primary Roman numerals (I–V or A,B,C) > '
     'Intermediate lowercase roman (i–v or a,b,c) > Minor in parens ((i),(ii)…) > Micro, nested '
     'arbitrarily deep — e.g. "(iii) of (c) of ii of C".'),
    (2, "Diagonals (overlap allowed)",
     "Ending/leading diagonals explain overlapping sub-waves (wave iv crossing into wave i's territory) "
     "inside a wave 5 or wave C — a recognized valid EW pattern where overlap is normally forbidden."),
    (3, "The .618 workhorse level",
     "The single most-used Fibonacci level, for both wave-2/B pullback entries and topping guesses. "
     ".382 and extension multiples (1.618-style) also appear, but .618 dominates the chat."),
    (4, "Basket confirmation",
     'NDX, MU, AAOI, NVDA, CRWD, ARM and AEHR are expected to sit in the same wave phase concurrently — '
     'cited as confidence-building when they "all play along perfectly," while still reading "each chart '
     'on its own" for precise levels.'),
    (5, "Cash-raise / buy-the-dip rhythm",
     "Raise cash or take profit as price nears a projected local top (end of wave ii/b); scale back in "
     "once the C-wave / wave-v bottom completes, and only once cash is available and existing positions "
     "are already strongly green."),
    (6, "Options overlay (tactical puts)",
     "Short-dated index options (e.g. QQQ puts, 8/14 and 8/21 expiries) are used as a tactical short "
     "overlay during the projected down-leg, layered on top of the cash/equity moves."),
    (7, "“Don't half-ass it” discipline",
     'Explicit self-warning that this approach "you can\'t half-ass because you will lose lots of money" '
     '— paired with open admission that counts get revised in real time ("monkey wrench," "plain stupid").'),
    (8, "Bullish big-picture framing",
     "Even bearish near-term calls sit inside a bullish frame: wave 1 up off the April 2026 low completed "
     "late June (MU tagged 1255); once the current wave 2 correction finishes, wave 3 is expected to run "
     "into year-end."),
]

CAVEATS = [
    ("Elliott Wave counts are subjective and get revised in real time.",
     "The chat itself moved the NDX bottom target five times in about ten days:",
     ["27000", "27500–28000", "27400", "27500–27600", "27200–27400", "26800–27000"]),
    ("Index proxies, not the index itself.",
     "The chat's “NDX” and “SPX” are futures/index instruments this tool can't fetch directly — "
     "<strong>QQQ</strong> and <strong>SPY</strong> stand in as real, tradable ETF proxies (their prices are "
     "NOT rescaled to the index's point level — treat each as its own instrument that tracks the same index). "
     "See the methodology panel for the full backtest limitations list (uniform threshold, no transaction "
     "costs, overlapping windows, modest sample size).", None),
    ("This is a live tool, not a fixed replay.",
     "Every ticker's chart, cascade, wave tree and backtest run against real daily OHLC fetched on selection "
     "(cached briefly to avoid hammering the API on every rerun) — unlike the original artifact this is built "
     "from, there's no embedded historical snapshot and no single-ticker-only limitation.", None),
]

METHODOLOGY_HTML = """
<h4>1. ZigZag pivot detection (high/low-based)</h4>
<p>A pending swing HIGH is tracked as the running maximum of bar <code>high</code> since the last confirmed
pivot; it confirms the moment some later bar's <code>low</code> falls θ% below that running high
(symmetric for a pending swing LOW, tracked via <code>low</code>, confirmed by a later bar's <code>high</code>
rising θ% above it). θ (the threshold-%) is user-adjustable per ticker via the chart's sensitivity
control, default 3.0%. Complexity is O(n) in the number of bars — one linear pass. Each pivot also records
the bar index at which its reversal past θ first became detectable (<code>confirm_idx</code>); everything
downstream (wave fits, cascades, the backtest) only ever uses a pivot's finalized price once that bar has
passed, which is what makes the backtest lookahead-free by construction.</p>

<h4>2. Impulse &amp; correction rule set</h4>
<ul>
<li><strong>Impulse (5-pivot run):</strong> wave 2 may not fully retrace wave 1 (checked directly on price);
wave 3 may not be the shortest of waves 1/3/5; wave 4 overlapping into wave 1's price territory is flagged
and the structure is reclassified as a <strong>diagonal</strong> (a recognized EW pattern that permits the
overlap) rather than rejected outright.</li>
<li><strong>Correction (3-pivot A-B-C):</strong> B must retrace 38.2%–78.6% of A.</li>
</ul>

<h4>3. Confidence-score formula (as actually implemented)</h4>
<p><strong>Impulse:</strong> <code>confidence = (closeness(retr2, [.382,.5,.618,.786])×0.30 +
closeness(retr4, [.236,.382,.5])×0.25 + closeness(ext5/1, [.618,1,1.618])×0.15 + 0.20 if wave3 not
shortest + 0.10 if wave2 doesn't fully retrace) × 100</code>, then ×0.85 if reclassified as a
diagonal. <code>closeness(ratio, targets) = clamp01(1 - minDistanceToNearestTarget/0.5)</code> — a ratio
exactly on a canonical Fibonacci level scores 1.0, one 0.5 away from every target scores 0.</p>
<p><strong>Correction:</strong> <code>confidence = clamp01(1 - min(|retrB-.5|,|retrB-.618|)/0.4)×70 + 30
if retrB is in [.382,.786]</code>.</p>
<p><strong>Backtest per-pivot confidence</strong> (a coarser grain — see §5): <code>closeness(|leg_i|/|leg_i-1|,
[.382,.5,.618,.786,1,1.272,1.618,2.618]) × 100</code> — the same <code>closeness()</code> primitive,
applied to the two-leg ratio at each pivot triple rather than a full 5- or 3-pivot fit.</p>

<h4>4. Fibonacci ratio sets</h4>
<p>Retracement: 0.382, 0.5, 0.618, 0.786. Extension: 1.0, 1.272, 1.618, 2.618. Both cascades (the live
"current cascade" panel and every backtest target) are generated by the same <code>fib_cascade(pivots, i)</code>
function: retracement levels measure back from pivot <code>p_i</code> by the just-completed leg
(<code>p_i-1 → p_i</code>); extension levels project forward from <code>p_i</code> using the length of
the prior leg (<code>p_i-2 → p_i-1</code>), in that leg's own direction.</p>

<h4>5. Walk-forward Fibonacci-target backtest — exact method</h4>
<ul>
<li>Uniform ZigZag threshold across the whole scanned universe: 3.0% (chosen once, not optimized per name —
this is deliberately NOT a curve-fit backtest, but it also isn't tuned for any individual ticker).</li>
<li>For every pivot p_i (i≥2) with a resolved <code>confirm_idx</code> — the still-forming trailing pivot
is excluded, since testing it would use information not yet knowable at that point in history.</li>
<li>Targets = <code>fib_cascade(pivots, i)</code>, called exactly as of p_i's confirmation bar.</li>
<li>Forward test window: W trading days (default 20, adjustable 5–60) starting the bar AFTER
<code>confirm_idx</code>. A pivot is skipped entirely if a FULL W-day window isn't available before the end
of the fetched history — this means the most recent few pivots in every ticker's history are never scored.</li>
<li>Hit test: any bar's <code>[low,high]</code> range intersects the target price ± tolerance (default
0.5%, adjustable 0.25–2%) at any point in the window. Hit ⇒ days-to-hit = bars from window start to
the first touch.</li>
<li><strong>No-lookahead justification:</strong> every target is generated only from data at or before its own
confirmation bar, and is only ever checked against strictly later bars. This is walk-forward by construction,
not by discipline.</li>
</ul>

<h4>6. Real limitations of this backtest (stated plainly, not oversold)</h4>
<ul>
<li>Threshold (3.0%) and tolerance band are fixed and applied uniformly — not optimized per ticker, but also
not validated as the "best" choice for any given name.</li>
<li>No transaction costs, slippage, spread, or borrow cost modeled anywhere.</li>
<li>Targets from overlapping pivots can test overlapping time windows, so hits are not fully independent
draws — treat the sample size N as an upper bound on genuinely independent evidence, not the true effective
sample size.</li>
<li>A few years of daily data per ticker is a modest sample, especially once split by ratio bucket or
confidence quartile — some cells in the breakdown tables below will have small N. Always read the N, not
just the %.</li>
<li>This measures whether a price level was TOUCHED within a window, not whether a trade built around it
would have been profitable net of stops, sizing, or the path taken to get there.</li>
</ul>

<h4>7. Data provenance</h4>
<p>Real daily OHLC via <code>yfinance</code> (free, no key), with an optional Alpha Vantage fallback — the
same data feed used everywhere else in this dashboard (see the Live Market tab). Every ticker fetches live on
selection, not from a fixed embedded snapshot — history length matches the "Backtest window" you've chosen in
the sidebar. <strong>QQQ</strong> and <strong>SPY</strong> are real, tradable ETFs standing in for the
Nasdaq-100 and S&amp;P 500/SPX futures/index instruments the source chat actually discussed — their prices
are shown at their own real level, never rescaled to pretend to be on NDX's/SPX's index-point scale.</p>

<h4>8. What this tool does NOT establish</h4>
<p>Elliott Wave counts remain inherently subjective and revised in real time — see the caveats panel and the
family chat's own revision history. Narrative explanations for why a market moved are not treated as a driver
anywhere in this tool — it is a pure price/pivot/ratio engine.</p>

<h4>9. Top Setups composite score — exact formula</h4>
<p>The Top Setups screener adds no new price-forecasting logic — it is purely an aggregation/ranking layer
over <code>compute_for_ticker</code>, <code>fib_cascade</code>, and <code>backtest_ticker</code>, the same
functions used everywhere else on this page. For each ticker, with <code>last_close</code> = the most recent
close and <code>cascade</code> = that ticker's current Fibonacci cascade:</p>
<ul>
<li><strong>Entry quality:</strong> <code>nearest_support</code> = the highest-priced <em>retracement</em>-kind
cascade entry ≤ <code>last_close</code> (no entry-quality bonus if none exists — <code>entry_score</code>
is 0, not an error). <code>entry_proximity_pct = |last_close − nearest_support.price| / last_close ×
100</code>. <code>entry_score = clamp01(1 − entry_proximity_pct/5) × 100</code> — within 5% of the
support level scores well, decaying linearly to 0 further away.</li>
<li><strong>Upside:</strong> <code>nearest_upside</code> = the lowest-priced <em>extension</em>-kind cascade
entry &gt; <code>last_close</code> (0 if none). <code>upside_pct = (nearest_upside.price − last_close) /
last_close × 100</code>.</li>
<li><strong>Invalidation (downside risk reference):</strong> if the current fit is an <strong>impulse</strong>,
invalidation = the price of the pivot at the fit's own start (the origin of the counted wave 1). If the
current fit is a <strong>correction</strong>, invalidation = the price 78.6% retraced from the correction's
A-leg start. If there is no current fit, invalidation = <code>nearest_support.price</code> if it exists, else
null. <code>downside_pct = |last_close − invalidation| / last_close × 100</code> (null if invalidation
is null).</li>
<li><strong>Risk/reward:</strong> <code>risk_reward = downside_pct &gt; 0 ? upside_pct/downside_pct :
(upside_pct &gt; 0 ? upside_pct/0.5 : 0)</code> — when there's no usable downside reference, the fallback
denominator is capped at 0.5 so a near-zero <code>downside_pct</code> can't blow the ratio up toward infinity.</li>
<li><strong>Confidence:</strong> the current fit's own <code>confidence</code> (0-100); 50 (neutral prior) if
there is no current fit — a ticker is never dropped from the rankings for lacking a fit, it just scores lower
via the other terms.</li>
<li><strong>Historical reliability</strong> (fallback tiers, checked in this order, always disclosed per-row):
(1) filter this ticker's own <code>backtest_ticker</code> records to the same ratio as
<code>nearest_upside.ratio</code> (or <code>nearest_support.ratio</code> if there's no upside target) — use
this sample's hit-rate if N ≥ 20 (tier: <em>ratio-specific</em>); (2) otherwise fall back to this ticker's
overall hit-rate across all its backtest records (tier: <em>ticker-overall</em>); (3) if the ticker has no
backtest records at all, fall back to the pooled hit-rate for that ratio across the scanned universe (tier:
<em>pooled all-universe</em>).</li>
<li><strong>Composite score</strong> (0-100, weights sum to 1.0): <code>score = 0.30×entry_score +
0.25×clamp01(risk_reward/3)×100 + 0.20×confidence + 0.15×historical_reliability +
0.10×clamp01(upside_pct/10)×100</code>. The scanned universe is ranked descending by this score; the
top 15 are shown as "Top Setups" and the bottom 10 as "Weakest Setups" (for transparency, so the panel isn't
one-sided).</li>
</ul>
<p>Unlike the original artifact this tool is built from — which ran its screener against a fixed embedded
snapshot because ranking 170 tickers against a live MCP connector on every tick wasn't practical (connector
rate limits, a 64-subscription cap) — this version fetches real data for every scanned ticker, subject to the
same short cache TTL used everywhere else in this dashboard. The universe defaults to a small, fast set for
responsiveness; expand it for a broader (slower) scan. The panel is explicitly not investment advice.</p>

<h4>10. Live feed</h4>
<p>Every ticker — not just one — fetches real daily OHLC through this dashboard's own data feed
(<code>yfinance</code>, with an optional Alpha Vantage fallback) when selected or included in a scan, cached
for a short TTL to avoid re-fetching on every rerun. There's no connector, no per-page subscription cap, and
no embedded snapshot to fall back to — if a fetch fails for a given ticker, that ticker is simply skipped with
its history length shown as unavailable, exactly as elsewhere in this app.</p>
"""
