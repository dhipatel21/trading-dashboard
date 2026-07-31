"""Visual chrome: custom CSS + small HTML components layered on top of Streamlit's
default widgets. Colors are the same validated palette used for the Plotly charts
(see src/theme.py) so the UI and the charts read as one system.
"""
import streamlit as st

from .theme import CATEGORICAL, GOOD, CRITICAL

BLUE = CATEGORICAL[0]
VIOLET = CATEGORICAL[6]
AQUA = CATEGORICAL[4]
WARNING = "#fab219"


def inject_css():
    st.markdown(f"""
    <style>
    .stApp {{
        background:
            radial-gradient(1200px 500px at 15% -10%, rgba(42,120,214,0.07), transparent 60%),
            radial-gradient(1000px 500px at 100% 0%, rgba(74,58,167,0.06), transparent 55%),
            #fcfcfb;
    }}

    /* ---- Hero banner ---- */
    .hero {{
        background: linear-gradient(120deg, {BLUE} 0%, #3a63c8 45%, {VIOLET} 100%);
        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 22px;
        box-shadow: 0 8px 24px rgba(42,120,214,0.18);
        color: #ffffff;
        position: relative;
        overflow: hidden;
    }}
    .hero::after {{
        content: "";
        position: absolute; inset: 0;
        background: radial-gradient(600px 200px at 90% 120%, rgba(255,255,255,0.14), transparent 60%);
        pointer-events: none;
    }}
    .hero h1 {{
        font-size: 1.9rem; font-weight: 750; margin: 0 0 4px 0; letter-spacing: -0.02em;
        color: #ffffff;
    }}
    .hero p {{
        margin: 0; font-size: 0.98rem; color: rgba(255,255,255,0.88); max-width: 640px;
    }}
    .live-badge {{
        display: inline-flex; align-items: center; gap: 7px;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.28);
        border-radius: 999px; padding: 5px 13px; margin-top: 14px;
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.02em; color: #fff;
    }}
    .live-dot {{
        width: 8px; height: 8px; border-radius: 50%; background: #4ee08a;
        box-shadow: 0 0 0 rgba(78,224,138,0.6);
        animation: pulse 1.8s infinite;
    }}
    @keyframes pulse {{
        0%   {{ box-shadow: 0 0 0 0 rgba(78,224,138,0.55); }}
        70%  {{ box-shadow: 0 0 0 8px rgba(78,224,138,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(78,224,138,0); }}
    }}

    /* ---- Section headers ---- */
    h3 {{ letter-spacing: -0.01em; }}

    /* ---- Metric cards ---- */
    div[data-testid="stMetric"] {{
        background: #ffffff;
        border: 1px solid rgba(11,11,11,0.06);
        border-radius: 14px;
        padding: 14px 16px 10px 16px;
        box-shadow: 0 1px 2px rgba(11,11,11,0.04), 0 6px 16px rgba(11,11,11,0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(11,11,11,0.06), 0 10px 24px rgba(11,11,11,0.07);
    }}
    div[data-testid="stMetricLabel"] {{ font-weight: 600; opacity: 0.65; }}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: rgba(11,11,11,0.03);
        padding: 6px;
        border-radius: 14px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 42px;
        border-radius: 10px;
        padding: 0 16px;
        font-weight: 600;
        color: #52514e;
    }}
    .stTabs [aria-selected="true"] {{
        background: #ffffff;
        color: {BLUE} !important;
        box-shadow: 0 1px 3px rgba(11,11,11,0.08);
    }}

    /* ---- Buttons ---- */
    .stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
        border: 1px solid rgba(11,11,11,0.08);
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(11,11,11,0.10);
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(120deg, {BLUE}, #2f5fc4);
        border: none;
        box-shadow: 0 4px 14px rgba(42,120,214,0.35);
    }}

    /* ---- Dataframes & tables ---- */
    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(11,11,11,0.06);
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background: #f7f8fb;
        border-right: 1px solid rgba(11,11,11,0.06);
    }}
    section[data-testid="stSidebar"] h1 {{
        font-size: 1.25rem;
    }}

    /* ---- Expanders (Methodology cards) ---- */
    details[data-testid="stExpander"] {{
        border-radius: 12px !important;
        border: 1px solid rgba(11,11,11,0.07) !important;
        box-shadow: 0 1px 2px rgba(11,11,11,0.03);
    }}

    /* ---- Category chips ---- */
    .chip {{
        display: inline-block; padding: 3px 11px; border-radius: 999px;
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.02em;
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)


def hero(title: str, subtitle: str, live: bool = True):
    badge = (
        '<div class="live-badge"><span class="live-dot"></span>LIVE DATA · streaming on refresh</div>'
        if live else ""
    )
    st.markdown(f"""
    <div class="hero">
        <h1>{title}</h1>
        <p>{subtitle}</p>
        {badge}
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
        f'border:1px solid {color}40;">{category.upper()}</span>'
    )
