"""Visual chrome: custom CSS + small HTML components layered on top of Streamlit's
default widgets. Dark, minimal, technical aesthetic — one accent color (blue),
monospace for data/numbers, flat surfaces, no soft gradients or emoji. Colors are
the same validated dark-mode palette used for the Plotly charts (see src/theme.py).
"""
import streamlit as st

from .theme import CATEGORICAL, GOOD, WARNING, CRITICAL, MONO_FONT

BLUE = CATEGORICAL[0]
VIOLET = CATEGORICAL[6]


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
