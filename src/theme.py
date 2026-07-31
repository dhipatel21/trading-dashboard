"""Shared Plotly theme: fixed-order categorical palette + sequential/diverging ramps.

Colors come from a validated colorblind-safe palette (OKLab CVD-checked). Hue
order is fixed and never re-cycled across charts — series keep the same color
wherever they appear.
"""
import plotly.graph_objects as go
import plotly.io as pio

CATEGORICAL = [
    "#2a78d6",  # 1 blue
    "#008300",  # 2 green
    "#e87ba4",  # 3 magenta
    "#eda100",  # 4 yellow
    "#1baf7a",  # 5 aqua
    "#eb6834",  # 6 orange
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]

SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95", "#0d366b"]
DIVERGING = ["#0d366b", "#2a78d6", "#9ec5f4", "#f0efec", "#f3a58c", "#e34948", "#8a1f1f"]

GOOD = "#0ca30c"
CRITICAL = "#d03b3b"

SURFACE_LIGHT = "#fcfcfb"
INK_LIGHT = "#0b0b0b"
MUTED_LIGHT = "#898781"
GRID_LIGHT = "#e1e0d9"


def register_template():
    template = go.layout.Template()
    template.layout = go.Layout(
        colorway=CATEGORICAL,
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", color=INK_LIGHT, size=13),
        paper_bgcolor=SURFACE_LIGHT,
        plot_bgcolor=SURFACE_LIGHT,
        xaxis=dict(gridcolor=GRID_LIGHT, zerolinecolor=GRID_LIGHT, linecolor=MUTED_LIGHT, showline=True),
        yaxis=dict(gridcolor=GRID_LIGHT, zerolinecolor=GRID_LIGHT, linecolor=MUTED_LIGHT, showline=True),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=50, r=20, t=40, b=40),
        hovermode="x unified",
    )
    pio.templates["dashboard"] = template
    pio.templates.default = "dashboard"
