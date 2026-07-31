"""Shared Plotly theme (dark mode): fixed-order categorical palette + sequential/diverging ramps.

Colors come from a validated colorblind-safe palette (OKLab CVD-checked), dark-mode
column. Hue order is fixed and never re-cycled across charts — series keep the same
color wherever they appear.
"""
import plotly.graph_objects as go
import plotly.io as pio

CATEGORICAL = [
    "#3987e5",  # 1 blue
    "#008300",  # 2 green
    "#d55181",  # 3 magenta
    "#c98500",  # 4 yellow
    "#199e70",  # 5 aqua
    "#d95926",  # 6 orange
    "#9085e9",  # 7 violet
    "#e66767",  # 8 red
]

DIVERGING = ["#184f95", "#3987e5", "#6da7ec", "#383835", "#e08f76", "#e66767", "#8a1f1f"]

GOOD = "#0ca30c"
WARNING = "#fab219"
SERIOUS = "#ec835a"
CRITICAL = "#e66767"

SURFACE_DARK = "#1a1a19"
PAGE_DARK = "#0a0a0b"
INK_DARK = "#ffffff"
SECONDARY_INK_DARK = "#c3c2b7"
MUTED_DARK = "#898781"
GRID_DARK = "#2c2c2a"
BASELINE_DARK = "#383835"

MONO_FONT = 'ui-monospace, "SF Mono", "Cascadia Code", "Roboto Mono", monospace'
SANS_FONT = "system-ui, -apple-system, Segoe UI, sans-serif"


def register_template():
    template = go.layout.Template()
    template.layout = go.Layout(
        colorway=CATEGORICAL,
        font=dict(family=SANS_FONT, color=SECONDARY_INK_DARK, size=12),
        paper_bgcolor=SURFACE_DARK,
        plot_bgcolor=SURFACE_DARK,
        xaxis=dict(gridcolor=GRID_DARK, zerolinecolor=GRID_DARK, linecolor=BASELINE_DARK, showline=True),
        yaxis=dict(gridcolor=GRID_DARK, zerolinecolor=GRID_DARK, linecolor=BASELINE_DARK, showline=True),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=SECONDARY_INK_DARK)),
        margin=dict(l=50, r=20, t=40, b=40),
        hovermode="x unified",
        title=dict(font=dict(color=INK_DARK, size=14)),
    )
    pio.templates["dashboard"] = template
    pio.templates.default = "dashboard"
