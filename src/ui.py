"""Visual chrome: custom CSS + small HTML components layered on top of Streamlit's
default widgets. Dark, minimal, technical aesthetic — one accent color (blue),
monospace for data/numbers, flat surfaces, no soft gradients or emoji. Colors are
the same validated dark-mode palette used for the Plotly charts (see src/theme.py).
"""
from __future__ import annotations
import streamlit as st

from .theme import CATEGORICAL, GOOD, WARNING, SERIOUS, CRITICAL, MONO_FONT, SANS_FONT

BLUE = CATEGORICAL[0]
VIOLET = CATEGORICAL[6]
PIVOT_HIGH = BLUE
PIVOT_LOW = CRITICAL


def inject_css():
    st.markdown(f"""
    <style>
    .stApp {{
        background:
            repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 32px),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 32px),
            #0a0a0b;
    }}

    * {{ scrollbar-width: thin; scrollbar-color: #2c2c2a #0a0a0b; }}
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: #0a0a0b; }}
    ::-webkit-scrollbar-thumb {{ background: #2c2c2a; border-radius: 5px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {BLUE}; }}

    /* ---- Page header ---- */
    .page-header {{
        display: flex;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        background: #111114;
        margin-bottom: 22px;
        overflow: hidden;
    }}
    .page-header-accent {{
        width: 4px;
        background: linear-gradient(180deg, {BLUE}, {VIOLET});
        flex-shrink: 0;
    }}
    .page-header-body {{ padding: 20px 26px; flex: 1; min-width: 0; }}
    .ph-title-row {{ display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }}
    .page-header h1 {{
        font-size: 1.4rem; font-weight: 700; margin: 0;
        letter-spacing: 0.02em; text-transform: uppercase; color: #ffffff;
    }}
    .page-header p {{
        margin: 8px 0 0 0; font-size: 0.92rem; color: #c3c2b7; max-width: 680px; line-height: 1.5;
    }}
    .live-chip {{
        display: inline-flex; align-items: center; gap: 7px;
        font-family: {MONO_FONT};
        font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em;
        color: #4ee08a;
        border: 1px solid rgba(78,224,138,0.35);
        background: rgba(78,224,138,0.08);
        border-radius: 4px; padding: 4px 10px;
        white-space: nowrap;
    }}
    .live-dot {{
        width: 7px; height: 7px; border-radius: 50%; background: #4ee08a;
        animation: pulse 1.8s infinite;
    }}
    @keyframes pulse {{
        0%   {{ box-shadow: 0 0 0 0 rgba(78,224,138,0.55); }}
        70%  {{ box-shadow: 0 0 0 7px rgba(78,224,138,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(78,224,138,0); }}
    }}

    /* ---- Section headers ---- */
    h3 {{
        font-size: 0.85rem !important; font-weight: 700 !important;
        text-transform: uppercase; letter-spacing: 0.06em; color: #ffffff !important;
        opacity: 0.92;
    }}

    /* ---- Metric cards ---- */
    div[data-testid="stMetric"] {{
        background: #111114;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 14px 16px 10px 16px;
        transition: border-color 0.15s ease;
    }}
    div[data-testid="stMetric"]:hover {{ border-color: rgba(57,135,229,0.45); }}
    div[data-testid="stMetricLabel"] {{
        font-weight: 700; opacity: 0.55; text-transform: uppercase; letter-spacing: 0.06em; font-size: 0.68rem !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: {MONO_FONT}; font-variant-numeric: tabular-nums;
    }}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 26px;
        background: transparent;
        padding: 0;
        border-bottom: 1px solid rgba(255,255,255,0.09);
        border-radius: 0;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 38px;
        border-radius: 0;
        padding: 0 2px;
        font-weight: 600;
        font-size: 0.78rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #898781;
        border-bottom: 2px solid transparent;
        background: transparent;
    }}
    .stTabs [aria-selected="true"] {{
        background: transparent !important;
        color: #ffffff !important;
        border-bottom: 2px solid {BLUE};
        box-shadow: none;
    }}

    /* ---- Buttons ---- */
    .stButton > button {{
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.02em;
        border: 1px solid rgba(255,255,255,0.14);
        background: #131316;
        color: #ffffff;
        transition: border-color 0.12s ease, box-shadow 0.12s ease;
    }}
    .stButton > button:hover {{
        border-color: {BLUE};
        box-shadow: 0 0 0 1px rgba(57,135,229,0.35);
        color: #ffffff;
    }}
    .stButton > button[kind="primary"] {{
        background: {BLUE};
        border: 1px solid {BLUE};
        color: #051224;
        font-weight: 700;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: #4f97ea;
        box-shadow: 0 0 18px rgba(57,135,229,0.4);
    }}

    /* ---- Dataframes & tables ---- */
    div[data-testid="stDataFrame"] {{
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }}
    div[data-testid="stDataFrame"] * {{
        font-family: {MONO_FONT} !important;
        font-variant-numeric: tabular-nums;
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background: #0d0d0f;
        border-right: 1px solid rgba(255,255,255,0.07);
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.85rem !important;
        color: #ffffff !important;
        opacity: 0.85;
    }}

    /* ---- Expanders (Methodology cards) ---- */
    details[data-testid="stExpander"] {{
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: #111114 !important;
    }}

    /* ---- Category chips ---- */
    .chip {{
        display: inline-block; padding: 3px 10px; border-radius: 4px;
        font-family: {MONO_FONT};
        font-size: 0.68rem; font-weight: 600; letter-spacing: 0.05em;
        margin-bottom: 10px;
    }}

    /* ================================================================
       Card / badge component language — ported from the Elliott Wave
       Tracker artifact (bordered + shadowed cards, status badges/pills,
       colored cascade rows, degree-colored wave tree), restyled for this
       app's dark palette. Used by the Elliott Wave tab; available anywhere.
       ================================================================ */
    .ew-card {{
        background: #111114;
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 4px 14px rgba(0,0,0,0.25);
        padding: 18px 20px;
        margin-bottom: 16px;
    }}
    .ew-card h2 {{
        font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;
        color: #c3c2b7; margin: 0 0 10px 0; font-weight: 700;
    }}
    .ew-muted {{ color: #898781; }}
    .ew-secondary {{ color: #c3c2b7; }}
    .ew-small {{ font-size: 0.78rem; }}

    .ew-badge {{
        display: inline-flex; align-items: center; gap: 6px; padding: 4px 11px; border-radius: 999px;
        font-size: 0.72rem; font-weight: 650; border: 1px solid transparent; white-space: nowrap;
    }}
    .ew-badge .dot {{ width: 7px; height: 7px; border-radius: 50%; flex: none; }}
    .ew-badge-good {{ background: rgba(12,163,12,0.16); color: #4ee08a; }}
    .ew-badge-good .dot {{ background: {GOOD}; }}
    .ew-badge-warning {{ background: rgba(250,178,25,0.16); color: #ffce6b; }}
    .ew-badge-warning .dot {{ background: {WARNING}; }}
    .ew-badge-serious {{ background: rgba(236,131,90,0.18); color: #ffb28e; }}
    .ew-badge-serious .dot {{ background: {SERIOUS}; }}
    .ew-badge-neutral {{ background: rgba(255,255,255,0.06); color: #c3c2b7; }}
    .ew-badge-neutral .dot {{ background: #898781; }}

    .ew-stat-chip {{
        border: 1px solid rgba(255,255,255,0.09); border-radius: 12px; padding: 10px 14px;
        display: flex; flex-direction: column; gap: 5px; background: #0d0d0f;
    }}
    .ew-stat-chip .label {{ font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; color: #898781; font-weight: 700; }}

    .ew-hr-tile {{
        border: 1px solid rgba(255,255,255,0.09); border-radius: 10px; padding: 12px 14px; background: #0d0d0f;
        flex: 1; min-width: 140px;
    }}
    .ew-hr-tile .value {{ font-family: {MONO_FONT}; font-size: 1.5rem; font-weight: 700; color: #fff; }}
    .ew-hr-tile .label {{ font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; color: #898781; font-weight: 700; margin-top: 2px; }}
    .ew-hr-tile .sub {{ font-size: 0.72rem; color: #c3c2b7; margin-top: 3px; }}

    .ew-cascade-row {{
        display: flex; justify-content: space-between; align-items: center; gap: 8px;
        padding: 8px 12px; border: 1px solid rgba(255,255,255,0.08); border-radius: 9px;
        font-size: 0.8rem; margin-bottom: 6px; background: #0d0d0f;
    }}
    .ew-cascade-row.retracement {{ border-left: 3px solid {PIVOT_LOW}; }}
    .ew-cascade-row.extension {{ border-left: 3px solid {PIVOT_HIGH}; }}
    .ew-cascade-row .price {{ font-family: {MONO_FONT}; font-weight: 700; }}
    .ew-cascade-row .ratio {{ color: #898781; font-size: 0.72rem; }}
    .ew-cascade-row .tag {{ color: #c3c2b7; font-size: 0.72rem; }}

    .ew-wtree, .ew-wtree ul {{ list-style: none; margin: 0; padding-left: 16px; }}
    .ew-wtree {{ padding-left: 0; }}
    .ew-wtree li {{ margin: 3px 0; padding: 5px 0 5px 12px; border-left: 2px solid #2c2c2a; }}
    .ew-wtree.degree-primary {{ border-left-color: {CATEGORICAL[0]}; }}
    .ew-wtree.degree-intermediate {{ border-left-color: {CATEGORICAL[4]}; }}
    .ew-wtree.degree-minor {{ border-left-color: {CATEGORICAL[3]}; }}
    .ew-wnode {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
    .ew-wnode .label {{ font-weight: 650; font-size: 0.8rem; color: #fff; }}
    .ew-wnode .desc {{ color: #c3c2b7; font-size: 0.72rem; }}
    .ew-wnode .current {{
        font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em;
        color: {GOOD}; border: 1px solid {GOOD}; border-radius: 999px; padding: 1px 7px;
    }}

    .ew-playbook-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px,1fr)); gap: 12px; margin-top: 6px; }}
    .ew-playbook-card {{ border: 1px solid rgba(255,255,255,0.08); border-radius: 11px; padding: 12px 14px; background: #0d0d0f; }}
    .ew-playbook-card .pnum {{ font-size: 0.68rem; color: #898781; font-weight: 700; }}
    .ew-playbook-card h4 {{ font-size: 0.8rem; margin: 4px 0 5px 0; color: #fff; }}
    .ew-playbook-card p {{ font-size: 0.74rem; color: #c3c2b7; margin: 0; line-height: 1.5; }}

    .ew-disclaimer {{
        display: flex; gap: 10px; align-items: flex-start; padding: 12px 14px; margin-bottom: 14px;
        border: 1px solid rgba(250,178,25,0.35); background: rgba(250,178,25,0.08);
        border-radius: 10px; font-size: 0.78rem; line-height: 1.55; color: #c3c2b7;
    }}
    .ew-disclaimer strong {{ color: #fff; }}
    .ew-disclaimer .icon {{
        flex: none; width: 20px; height: 20px; border-radius: 50%; background: {WARNING};
        color: #3a2600; font-weight: 800; font-size: 12px; display: flex; align-items: center;
        justify-content: center; margin-top: 1px;
    }}

    .ew-revision-chain {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 8px; font-size: 0.75rem; }}
    .ew-revision-chip {{ border: 1px solid rgba(255,255,255,0.12); border-radius: 7px; padding: 3px 9px; font-family: {MONO_FONT}; color: #c3c2b7; }}
    .ew-revision-arrow {{ color: #898781; }}

    .ew-outcome-badge {{
        display: inline-flex; align-items: center; font-size: 0.68rem; font-weight: 650;
        padding: 2px 8px; border-radius: 999px; white-space: nowrap;
    }}
    .ew-outcome-hit {{ background: rgba(12,163,12,0.16); color: #4ee08a; }}
    .ew-outcome-revised {{ background: rgba(236,131,90,0.18); color: #ffb28e; }}
    .ew-outcome-excluded {{ background: rgba(255,255,255,0.06); color: #898781; }}

    .ew-methodology {{ font-size: 0.82rem; line-height: 1.6; color: #c3c2b7; }}
    .ew-methodology h4 {{ font-size: 0.82rem; color: #fff; margin: 16px 0 4px; }}
    .ew-methodology h4:first-child {{ margin-top: 0; }}
    .ew-methodology code {{ background: rgba(255,255,255,0.08); border-radius: 4px; padding: 1px 5px; font-size: 0.76rem; font-family: {MONO_FONT}; }}
    .ew-methodology ul {{ margin: 4px 0 8px; padding-left: 20px; }}
    .ew-methodology li {{ margin-bottom: 4px; }}
    .ew-methodology strong {{ color: #fff; }}
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, live: bool = True):
    chip = '<span class="live-chip"><span class="live-dot"></span>LIVE</span>' if live else ""
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-accent"></div>
        <div class="page-header-body">
            <div class="ph-title-row">
                <h1>{title}</h1>
                {chip}
            </div>
            <p>{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


CATEGORY_COLORS = {
    "Trend Following": CATEGORICAL[0],
    "Mean Reversion": CATEGORICAL[2],
    "Mean Reversion / Statistical": CATEGORICAL[4],
    "Momentum": CATEGORICAL[5],
    "Machine Learning": CATEGORICAL[6],
    "Deep Learning": CATEGORICAL[3],
    "Reinforcement Learning": CATEGORICAL[7],
    "Benchmark": "#898781",
}


def category_chip(category: str) -> str:
    color = CATEGORY_COLORS.get(category, "#898781")
    return (
        f'<span class="chip" style="background:{color}1a; color:{color};'
        f'border:1px solid {color}55;">{category.upper()}</span>'
    )


# ----------------------------------------------------------------------------
# Card/badge component helpers (Elliott Wave tab visual language)
# ----------------------------------------------------------------------------
def ew_badge(text: str, kind: str = "neutral") -> str:
    """kind: good | warning | serious | neutral"""
    return f'<span class="ew-badge ew-badge-{kind}"><span class="dot"></span>{text}</span>'


def ew_stat_chip(label: str, value_html: str) -> str:
    return f'<div class="ew-stat-chip"><span class="label">{label}</span>{value_html}</div>'


def ew_hr_tile(value: str, label: str, sub: str = "") -> str:
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="ew-hr-tile"><div class="value">{value}</div><div class="label">{label}</div>{sub_html}</div>'


def ew_cascade_row(kind: str, ratio_label: str, price: str, tag: str) -> str:
    return f"""<div class="ew-cascade-row {kind}">
        <div><span class="price">${price}</span> <span class="tag">{tag}</span></div>
        <span class="ratio">{ratio_label}</span>
    </div>"""


def ew_playbook_card(n: int, title: str, text: str) -> str:
    return f"""<div class="ew-playbook-card">
        <span class="pnum">#{n}</span>
        <h4>{title}</h4>
        <p>{text}</p>
    </div>"""


def ew_disclaimer(html: str) -> str:
    return f'<div class="ew-disclaimer"><span class="icon">!</span><div>{html}</div></div>'


def ew_outcome_badge(resolution: str) -> str:
    label = {"hit": "Hit", "revised": "Revised", "excluded": "Pending / standing"}.get(resolution, resolution)
    cls = {"hit": "hit", "revised": "revised", "excluded": "excluded"}.get(resolution, "excluded")
    return f'<span class="ew-outcome-badge ew-outcome-{cls}">{label}</span>'


def ew_revision_chain(steps: list[str]) -> str:
    parts = []
    for i, s in enumerate(steps):
        if i:
            parts.append('<span class="ew-revision-arrow">→</span>')
        parts.append(f'<span class="ew-revision-chip">{s}</span>')
    return f'<div class="ew-revision-chain">{"".join(parts)}</div>'


def ew_card_open(title: str | None = None) -> str:
    heading = f"<h2>{title}</h2>" if title else ""
    return f'<div class="ew-card">{heading}'


def ew_card_close() -> str:
    return "</div>"
