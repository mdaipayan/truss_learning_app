"""Responsive, interactive Learn page for Truss Learning.

The parent app owns XP, persistence, and routing. This module receives tutorial
content and callbacks instead of importing main.py or mutating game state.
"""
from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import plotly.graph_objects as go
import streamlit as st

Tutorial = Mapping[str, Any]
IndexCallback = Callable[[int], None]
OptionalRenderer = Callable[[], None]

BASIC_NODES: dict[str, tuple[float, float]] = {
    "A": (0.0, 0.0), "B": (4.0, 0.0), "C": (2.0, 2.35),
}
BASIC_MEMBERS: tuple[tuple[str, str, str], ...] = (
    ("A", "B", "Bottom Chord"),
    ("A", "C", "Left Rafter / Top Chord"),
    ("C", "B", "Right Rafter / Top Chord"),
)
ASSUMPTIONS = [
    "Members are straight, pin-connected, two-force members carrying axial force.",
    "Ideal truss members carry tension or compression; bending is neglected.",
    "External loads are applied at joints in the ideal truss model.",
    "The determinacy count is not proof of geometric stability.",
]

FORMULAS: dict[str, list[tuple[str, str]]] = {
    "What is a Truss?": [
        ("Planar truss determinacy check", r"m+r=2j"),
    ],
    "Method of Joints": [
        ("Horizontal equilibrium", r"\sum F_x=0"),
        ("Vertical equilibrium", r"\sum F_y=0"),
    ],
    "Method of Sections": [
        ("Equilibrium of a cut section", r"\sum F_x=0,\quad \sum F_y=0,\quad \sum M=0"),
    ],
    "Determinacy and Stability": [
        ("Degree of static indeterminacy (count)", r"i=m+r-2j"),
        ("Determinate by count", r"m+r=2j"),
        ("Indeterminate by count", r"m+r>2j"),
        ("Insufficient constraints by count", r"m+r<2j"),
        ("Simple triangular-truss example", r"m=3,\quad r=3,\quad j=3,\quad m+r=6=2j"),
    ],
    "Determinacy and Truss Optimization": [
        ("Material-volume objective", r"\min_{\{A_i\}} V=\sum_i L_iA_i"),
        ("Axial stress constraint", r"|\sigma_i|=\left|\frac{P_i}{A_i}\right|\leq \sigma_{\mathrm{allow}}"),
        ("Displacement constraint", r"\|\mathbf{u}_j\|\leq \delta_{\mathrm{allow}}"),
        ("Redundant member axial stiffness", r"k_i=\frac{E_iA_i}{L_i}"),
    ],
}

LEARN_CSS = r"""
<style>
.st-key-learn_page { color: #0f172a; }
.st-key-learn_page .learn-eyebrow {
  color:#2563eb; font-size:.78rem; font-weight:800; letter-spacing:.1em;
  text-transform:uppercase; margin-bottom:.4rem;
}
.st-key-learn_page .learn-intro {
  color:#475569; font-size:1rem; line-height:1.65; margin:.2rem 0 1rem;
}
.st-key-learn_page .learn-panel {
  padding:1rem 1.05rem; border:1px solid #e2e8f0; border-radius:16px;
  background:#fff; box-shadow:0 3px 12px rgba(15,23,42,.035); margin-bottom:.7rem;
}
.st-key-learn_page .learn-formula-label {
  color:#1d4ed8; font-size:.76rem; font-weight:800; letter-spacing:.07em;
  text-transform:uppercase; margin:.3rem 0;
}
.st-key-learn_page .stButton > button {
  min-height:2.7rem; border-radius:10px; font-weight:650;
  white-space:normal; overflow-wrap:anywhere;
}
.st-key-learn_page [data-testid="stPlotlyChart"] { max-width:100%; }
.st-key-learn_page .learn-muted { color:#64748b; font-size:.83rem; line-height:1.5; }
@media (max-width:768px) {
  .st-key-learn_page [data-testid="stHorizontalBlock"] {
    display:flex !important; flex-wrap:wrap !important; align-items:stretch !important;
    gap:.75rem !important; width:100% !important;
  }
  .st-key-learn_page [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex:1 1 100% !important; width:100% !important; min-width:100% !important;
    max-width:100% !important; box-sizing:border-box !important;
  }
  .st-key-learn_page .learn-panel { padding:.85rem; border-radius:13px; }
  .st-key-learn_page .stButton > button { width:100%; min-height:2.85rem; }
}
@media (prefers-reduced-motion:reduce) {
  .st-key-learn_page * { transition:none !important; scroll-behavior:auto !important; }
}
</style>
"""


def _clean_content(text: str) -> str:
    """Convert legacy content markup to Markdown without leaving equations unformatted."""
    text = re.sub(r"\[/?[^\]]+\]", "", text).strip()

    # Formula cards display these equations with st.latex; keep prose in the body.
    text = text.replace("m + r = 2j", "the determinate-count condition")
    text = text.replace("m + r < 2j", "the count indicates insufficient constraints")
    text = text.replace("m + r > 2j", "the count indicates indeterminacy")
    text = text.replace("ΣFx=0, ΣFy=0, ΣM=0", "force and moment equilibrium")
    text = text.replace("ΣFx = 0, ΣFy = 0, ΣM = 0", "force and moment equilibrium")
    text = text.replace("ΣFx=0, ΣFy=0", "horizontal and vertical force equilibrium")
    text = text.replace("ΣFx = 0 and ΣFy = 0", "horizontal and vertical force equilibrium")
    text = text.replace("ΣFx = 0", "horizontal force equilibrium")
    text = text.replace("ΣFy = 0", "vertical force equilibrium")
    text = re.sub(
        r"Example: A simple triangular truss with pin \+ roller support:\s*"
        r"m = 3, r = 3, j = 3\s*→\s*3 \+ 3 = 2\(3\) = 6\s*✓ Determinate",
        "Example: A simple triangular truss with three members and three reactions meets the determinate counting condition.",
        text,
        flags=re.IGNORECASE,
    )
    text = text.replace("Minimize material volume: V = Σ(Lᵢ Aᵢ)",
                        "Minimize material volume based on member lengths and areas.")
    text = text.replace("subject to limits such as |σᵢ| ≤ σ_allow and δ_max ≤ δ_allow.",
                        "subject to axial-stress and displacement limits.")
    output = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("• "):
            line = "- " + line[2:]
        if not line:
            output.append("")
            continue
        output.append(line)
    return "\n".join(output)


def _add_member(
    fig: go.Figure, nodes: Mapping[str, tuple[float, float]],
    start: str, end: str, label: str, *,
    color: str = "#1e3a5f", width: float = 3.5, dash: str = "solid",
) -> None:
    """Add a labelled structural member with a useful hover target."""
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    fig.add_trace(go.Scatter(
        x=[x1, x2], y=[y1, y2], mode="lines",
        line={"color": color, "width": width, "dash": dash},
        name=label, showlegend=False,
        customdata=[[label, start, end], [label, start, end]],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "From joint %{customdata[1]} to %{customdata[2]}<extra></extra>"
        ),
    ))


def _add_nodes(
    fig: go.Figure,
    nodes: Mapping[str, tuple[float, float]],
    highlight: str | None = None,
) -> None:
    """Draw crisp joints with hover coordinates and readable labels."""
    names = list(nodes)
    fig.add_trace(go.Scatter(
        x=[nodes[name][0] for name in names],
        y=[nodes[name][1] for name in names],
        mode="markers+text", text=names, textposition="top center",
        textfont={"size": 11, "color": "#0f172a", "family": "Arial, sans-serif"},
        marker={
            "size": [15 if name == highlight else 10 for name in names],
            "color": ["#f59e0b" if name == highlight else "#2563eb" for name in names],
            "line": {"color": "#ffffff", "width": 1.5},
        },
        customdata=[[name, nodes[name][0], nodes[name][1]] for name in names],
        hovertemplate=(
            "<b>Joint %{customdata[0]}</b><br>"
            "x = %{customdata[1]:.2f} m<br>"
            "y = %{customdata[2]:.2f} m<extra></extra>"
        ),
        name="Joints", showlegend=False,
    ))


def _add_supports(
    fig: go.Figure,
    nodes: Mapping[str, tuple[float, float]],
    support_names: Sequence[str],
) -> None:
    """Add schematic pin/roller symbols and ground hatching below support joints."""
    if not support_names:
        return
    fig.add_trace(go.Scatter(
        x=[nodes[name][0] for name in support_names],
        y=[nodes[name][1] - 0.17 for name in support_names],
        mode="markers",
        marker={
            "symbol": "triangle-up", "size": 19, "color": "#475569",
            "line": {"color": "#ffffff", "width": 1},
        },
        name="Supports", showlegend=False, hoverinfo="skip",
    ))
    for name in support_names:
        x, y = nodes[name]
        ground_y = y - 0.38
        fig.add_shape(
            type="line", x0=x - 0.28, y0=ground_y,
            x1=x + 0.28, y1=ground_y,
            line={"color": "#475569", "width": 2},
        )
        for tick in range(5):
            x0 = x - 0.22 + tick * 0.11
            fig.add_shape(
                type="line", x0=x0, y0=ground_y,
                x1=x0 - 0.09, y1=ground_y - 0.10,
                line={"color": "#64748b", "width": 1},
            )


def _add_force_arrow(
    fig: go.Figure,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str,
    *,
    color: str = "#92400e",
    label_position: tuple[float, float] | None = None,
    width: float = 2.2,
) -> None:
    """Draw a vector arrow and place its label independently to avoid overlap."""
    fig.add_annotation(
        x=end[0], y=end[1], ax=start[0], ay=start[1],
        xref="x", yref="y", axref="x", ayref="y",
        text="", showarrow=True, arrowhead=3, arrowsize=1.15,
        arrowwidth=width, arrowcolor=color,
    )
    if label:
        lx, ly = label_position or (
            (start[0] + end[0]) / 2 + 0.12,
            (start[1] + end[1]) / 2 + 0.12,
        )
        fig.add_annotation(
            x=lx, y=ly, text=f"<b>{label}</b>", showarrow=False,
            font={"size": 11, "color": color},
            bgcolor="rgba(255,255,255,0.92)", borderpad=1,
        )


def _add_dimension(
    fig: go.Figure, x1: float, x2: float, y: float, label: str,
) -> None:
    fig.add_shape(
        type="line", x0=x1, y0=0, x1=x1, y1=y,
        line={"color": "#94a3b8", "width": 1, "dash": "dot"},
    )
    fig.add_shape(
        type="line", x0=x2, y0=0, x1=x2, y1=y,
        line={"color": "#94a3b8", "width": 1, "dash": "dot"},
    )
    fig.add_annotation(
        x=x2, y=y, ax=x1, ay=y, xref="x", yref="y", axref="x", ayref="y",
        text="", showarrow=True, arrowhead=2, arrowside="end+start",
        arrowwidth=1.3, arrowcolor="#64748b",
    )
    fig.add_annotation(
        x=(x1 + x2) / 2, y=y - 0.13, text=label, showarrow=False,
        font={"size": 10, "color": "#475569"},
        bgcolor="rgba(255,255,255,0.92)", borderpad=1,
    )


def _layout(
    fig: go.Figure,
    title: str,
    *,
    height: int = 390,
    x_range: tuple[float, float] | None = None,
    y_range: tuple[float, float] | None = None,
    equal_scale: bool = True,
) -> go.Figure:
    """Consistent white technical drawing canvas with axes hidden."""
    fig.update_layout(
        title={"text": f"<b>{title}</b>", "x": 0.02, "xanchor": "left",
               "font": {"size": 16, "color": "#0f172a"}},
        autosize=True, height=height,
        margin={"l": 8, "r": 8, "t": 52, "b": 8},
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font={"family": "Inter, Arial, sans-serif", "size": 12, "color": "#0f172a"},
        hoverlabel={"bgcolor": "#ffffff", "font_size": 13},
        showlegend=False,
    )
    fig.update_xaxes(
        visible=False, showgrid=False, zeroline=False, fixedrange=True,
        range=list(x_range) if x_range else None,
    )
    fig.update_yaxes(
        visible=False, showgrid=False, zeroline=False, fixedrange=True,
        range=list(y_range) if y_range else None,
    )
    if equal_scale:
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def _basic_figure() -> go.Figure:
    """Topic 1: an annotated roof truss with supports, loads, reactions and span."""
    fig = go.Figure()
    nodes = BASIC_NODES
    for start, end, label in BASIC_MEMBERS:
        _add_member(fig, nodes, start, end, label, width=4.0)
    _add_supports(fig, nodes, ("A", "B"))
    _add_nodes(fig, nodes)
    _add_force_arrow(fig, (2.0, 3.05), (2.0, 2.48), "P",
                     label_position=(2.20, 2.82), color="#92400e")
    _add_force_arrow(fig, (0.0, 0.0), (0.0, 0.63), "Ay",
                     label_position=(-0.23, 0.43), color="#6d28d9")
    _add_force_arrow(fig, (0.0, 0.0), (0.62, 0.0), "Ax",
                     label_position=(0.40, 0.19), color="#6d28d9")
    _add_force_arrow(fig, (4.0, 0.0), (4.0, 0.63), "By",
                     label_position=(4.22, 0.43), color="#6d28d9")
    fig.add_annotation(
        x=0.0, y=-0.57, text="<b>PIN</b>", showarrow=False,
        font={"size": 9, "color": "#475569"},
    )
    fig.add_annotation(
        x=4.0, y=-0.57, text="<b>ROLLER</b>", showarrow=False,
        font={"size": 9, "color": "#475569"},
    )
    _add_dimension(fig, 0.0, 4.0, -0.83, "4.0 m span")
    return _layout(
        fig, "Simple triangular roof truss", height=430,
        x_range=(-0.75, 4.75), y_range=(-1.18, 3.32),
    )


def _types_figure() -> go.Figure:
    """Topic 2: compact Pratt, Warren and Howe layouts with distinct load paths."""
    fig = go.Figure()
    offset_pratt, offset_warren, offset_howe = 0.0, 4.35, 8.70

    def add_chord(nodes: Mapping[str, tuple[float, float]], names: Sequence[str],
                  label: str, color: str = "#1e3a5f") -> None:
        for left, right in zip(names, names[1:]):
            _add_member(fig, nodes, left, right, f"{label}: {left}-{right}",
                        color=color, width=2.6)

    def add_panel(title: str, offset: float, kind: str) -> None:
        bottom = [(offset + i, 0.0) for i in range(4)]
        top = [(offset + i, 0.55) for i in range(4)]
        if kind == "Warren":
            top = [(offset + 0.5, 0.55), (offset + 1.5, 0.55),
                   (offset + 2.5, 0.55)]
            names = [f"W{i}" for i in range(4)] + [f"WT{i}" for i in range(3)]
            points = bottom + top
            nodes = {name: point for name, point in zip(names, points)}
            bottom_names = names[:4]
            upper_names = names[4:]
            add_chord(nodes, bottom_names, "Bottom chord")
            zigzag = [
                (bottom_names[0], upper_names[0]), (upper_names[0], bottom_names[1]),
                (bottom_names[1], upper_names[1]), (upper_names[1], bottom_names[2]),
                (bottom_names[2], upper_names[2]), (upper_names[2], bottom_names[3]),
            ]
            for a, b in zigzag:
                _add_member(fig, nodes, a, b, f"Warren diagonal {a}-{b}",
                            color="#d97706", width=2.8)
            _add_supports(fig, nodes, (bottom_names[0], bottom_names[-1]))
        else:
            nodes = {
                **{f"{kind}B{i}": point for i, point in enumerate(bottom)},
                **{f"{kind}T{i}": point for i, point in enumerate(top)},
            }
            b_names = [f"{kind}B{i}" for i in range(4)]
            t_names = [f"{kind}T{i}" for i in range(4)]
            add_chord(nodes, b_names, "Bottom chord")
            add_chord(nodes, t_names, "Top chord")
            for i in range(4):
                _add_member(fig, nodes, b_names[i], t_names[i], f"Vertical {i+1}",
                            color="#64748b", width=2.2)
            for i in range(3):
                if kind == "Pratt":
                    a, b = t_names[i], b_names[i + 1]
                    diag_color = "#15803d"
                else:
                    a, b = b_names[i], t_names[i + 1]
                    diag_color = "#b91c1c"
                _add_member(fig, nodes, a, b, f"{kind} diagonal {a}-{b}",
                            color=diag_color, width=2.8)
            _add_supports(fig, nodes, (b_names[0], b_names[-1]))
        _add_nodes(fig, nodes)
        fig.add_annotation(
            x=offset + 1.5, y=1.13, text=f"<b>{title} truss</b>",
            showarrow=False, font={"size": 12, "color": "#1d4ed8"},
        )
        note = {
            "Pratt": "Diagonals highlighted green",
            "Warren": "Alternating triangular web",
            "Howe": "Opposite diagonal direction",
        }[title]
        fig.add_annotation(
            x=offset + 1.5, y=-0.48, text=note, showarrow=False,
            font={"size": 9, "color": "#475569"},
        )

    add_panel("Pratt", offset_pratt, "Pratt")
    add_panel("Warren", offset_warren, "Warren")
    add_panel("Howe", offset_howe, "Howe")
    return _layout(
        fig, "Compare common planar truss configurations", height=365,
        x_range=(-0.55, 12.95), y_range=(-0.62, 1.38), equal_scale=False,
    )


def _joints_figure() -> go.Figure:
    """Topic 3: a multi-panel truss highlighting the start joint for analysis."""
    nodes = {
        "A": (0.0, 0.0), "B": (1.5, 0.0), "C": (3.0, 0.0), "D": (4.5, 0.0),
        "E": (0.0, 0.78), "F": (1.5, 0.78), "G": (3.0, 0.78), "H": (4.5, 0.78),
    }
    members = [
        ("A", "B", "Bottom chord AB"), ("B", "C", "Bottom chord BC"),
        ("C", "D", "Bottom chord CD"), ("E", "F", "Top chord EF"),
        ("F", "G", "Top chord FG"), ("G", "H", "Top chord GH"),
        ("A", "E", "Vertical AE"), ("B", "F", "Vertical BF"),
        ("C", "G", "Vertical CG"), ("D", "H", "Vertical DH"),
        ("E", "B", "Diagonal EB"), ("F", "C", "Diagonal FC"),
        ("G", "D", "Diagonal GD"),
    ]
    fig = go.Figure()
    for start, end, label in members:
        _add_member(
            fig, nodes, start, end, label,
            color="#f59e0b" if "A" in (start, end) else "#1e3a5f",
            width=3.8 if "A" in (start, end) else 2.5,
        )
    _add_supports(fig, nodes, ("A", "D"))
    _add_nodes(fig, nodes, highlight="A")
    _add_force_arrow(fig, (1.5, 1.45), (1.5, 0.95), "P₁",
                     label_position=(1.76, 1.26))
    _add_force_arrow(fig, (3.0, 1.45), (3.0, 0.95), "P₂",
                     label_position=(3.25, 1.26))
    _add_force_arrow(fig, (0.0, 0.0), (0.0, 0.48), "Ay",
                     label_position=(-0.22, 0.31), color="#6d28d9")
    _add_force_arrow(fig, (4.5, 0.0), (4.5, 0.48), "Dy",
                     label_position=(4.72, 0.31), color="#6d28d9")
    fig.add_annotation(
        x=2.2, y=1.72,
        text="<b>Start at a joint with two or fewer unknowns</b>",
        showarrow=False, font={"size": 10, "color": "#92400e"},
        bgcolor="#fffbeb", bordercolor="#f59e0b", borderpad=4,
    )
    return _layout(
        fig, "Method of Joints — identify a solvable joint", height=390,
        x_range=(-0.7, 5.4), y_range=(-0.75, 2.0), equal_scale=False,
    )


def _joints_fbd_figure() -> go.Figure:
    """Free-body diagram: all assumed force vectors act away from joint A."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers+text", text=["A"],
        textposition="middle center",
        textfont={"size": 13, "color": "#0f172a"},
        marker={"size": 24, "color": "#fef3c7",
                "line": {"color": "#f59e0b", "width": 2}},
        name="Joint A", hovertemplate="<b>Joint A</b><extra></extra>",
    ))
    _add_force_arrow(fig, (0, 0), (-1.2, 0), "Ax",
                     label_position=(-0.75, 0.22), color="#6d28d9")
    _add_force_arrow(fig, (0, 0), (0, 1.05), "Ay",
                     label_position=(0.22, 0.75), color="#6d28d9")
    _add_force_arrow(fig, (0, 0), (1.25, 0), "F_AB (T)",
                     label_position=(0.78, 0.24), color="#15803d")
    _add_force_arrow(fig, (0, 0), (0.85, 0.78), "F_AE (T)",
                     label_position=(1.15, 0.79), color="#15803d")
    fig.add_annotation(
        x=0.0, y=-0.55, text="Assume tension: member forces pull away from the joint.",
        showarrow=False, font={"size": 10, "color": "#475569"},
    )
    return _layout(
        fig, "Free-body diagram of joint A", height=285,
        x_range=(-1.75, 1.9), y_range=(-0.85, 1.45),
    )


def _sections_figure() -> go.Figure:
    """Topic 4: a section cut crosses three highlighted unknown member forces."""
    nodes = {
        "A": (0.0, 0.0), "B": (1.0, 0.0), "C": (2.0, 0.0),
        "D": (3.0, 0.0), "E": (4.0, 0.0),
        "F": (0.0, 1.0), "G": (1.0, 1.0), "H": (2.0, 1.0),
        "I": (3.0, 1.0), "J": (4.0, 1.0),
    }
    members: list[tuple[str, str, str]] = []
    members.extend((a, b, "Bottom chord") for a, b in zip(("A","B","C","D"), ("B","C","D","E")))
    members.extend((a, b, "Top chord") for a, b in zip(("F","G","H","I"), ("G","H","I","J")))
    members.extend((a, b, "Vertical") for a, b in (("A","F"),("B","G"),("C","H"),("D","I"),("E","J")))
    members.extend((a, b, "Diagonal") for a, b in (("A","G"),("B","H"),("C","I"),("D","J")))
    cut_pairs = {("B", "C"), ("G", "H"), ("B", "H")}
    fig = go.Figure()
    for start, end, member_type in members:
        key = (start, end)
        reverse_key = (end, start)
        on_cut = key in cut_pairs or reverse_key in cut_pairs
        right_side = nodes[start][0] > 1.5 and nodes[end][0] > 1.5
        color = "#dc2626" if on_cut else "#cbd5e1" if right_side else (
            "#64748b" if member_type == "Vertical" else "#1e3a5f"
        )
        _add_member(
            fig, nodes, start, end, f"{member_type}: {start}-{end}",
            color=color, width=4.0 if on_cut else 2.5,
        )
    _add_supports(fig, nodes, ("A", "E"))
    _add_nodes(fig, nodes)
    _add_force_arrow(fig, (2.0, 1.7), (2.0, 1.18), "P",
                     label_position=(2.2, 1.48))
    _add_force_arrow(fig, (0.0, 0.0), (0.0, 0.44), "Ay",
                     label_position=(-0.2, 0.28), color="#6d28d9")
    _add_force_arrow(fig, (4.0, 0.0), (4.0, 0.44), "Ey",
                     label_position=(4.2, 0.28), color="#6d28d9")
    fig.add_shape(
        type="line", x0=1.5, y0=-0.12, x1=1.5, y1=1.25,
        line={"color": "#dc2626", "width": 2, "dash": "dash"},
    )
    fig.add_annotation(
        x=1.5, y=1.37, text="<b>Section cut</b>", showarrow=False,
        font={"size": 10, "color": "#b91c1c"},
    )
    for x, y, label in ((1.5, 1.08, "F₁"), (1.65, 0.49, "F₂"), (1.5, -0.18, "F₃")):
        fig.add_annotation(
            x=x, y=y, text=f"<b>{label}</b>", showarrow=False,
            font={"size": 10, "color": "#b91c1c"},
            bgcolor="rgba(255,255,255,0.95)", bordercolor="#fecaca", borderpad=2,
        )
    fig.add_annotation(
        x=0.45, y=1.48, text="Analyse the left section",
        showarrow=False, font={"size": 10, "color": "#1e3a5f"},
        bgcolor="#eff6ff", bordercolor="#bfdbfe", borderpad=3,
    )
    return _layout(
        fig, "Method of Sections — cut through at most three unknowns",
        height=430, x_range=(-0.65, 4.7), y_range=(-0.78, 2.0),
    )


def _determinacy_figure() -> go.Figure:
    """Topic 5: compare stable determinate, redundant and unstable topologies."""
    fig = go.Figure()
    cases = [
        (0.0, "DETERMINATE", "#15803d", "One diagonal", "m + r = 2j"),
        (3.0, "INDETERMINATE", "#b45309", "Two diagonals", "m + r > 2j"),
        (6.0, "UNSTABLE", "#b91c1c", "No diagonal", "m + r < 2j"),
    ]
    for offset, title, color, subtitle, formula in cases:
        nodes = {
            "A": (offset, 0.0), "B": (offset + 2.0, 0.0),
            "C": (offset + 2.0, 0.45), "D": (offset, 0.45),
        }
        for start, end, label in (
            ("A","B","Bottom chord"), ("B","C","Right vertical"),
            ("C","D","Top chord"), ("D","A","Left vertical"),
        ):
            _add_member(fig, nodes, start, end, f"{title}: {label}", width=2.7)
        if title != "UNSTABLE":
            _add_member(fig, nodes, "A", "C", f"{title}: diagonal AC",
                        color=color, width=3.3)
        if title == "INDETERMINATE":
            _add_member(fig, nodes, "B", "D", "Redundant diagonal BD",
                        color="#d97706", width=3.3)
        _add_supports(fig, nodes, ("A", "B"))
        _add_nodes(fig, {f"{name}{int(offset)}": point for name, point in nodes.items()})
        fig.add_annotation(
            x=offset + 1.0, y=1.23,
            text=f"<b>{title}</b><br>{formula}<br>{subtitle}",
            showarrow=False, align="center",
            font={"size": 10, "color": color},
            bgcolor="#ffffff", bordercolor=color, borderpad=4,
        )
    return _layout(
        fig, "Static determinacy is a count — stability still matters",
        height=425, x_range=(-0.55, 8.55), y_range=(-0.64, 1.85),
        equal_scale=False,
    )


def _optimization_figure() -> go.Figure:
    """Topic 6: sizing-design topology with the added redundant member emphasized."""
    nodes = {
        "A": (0.0, 0.0), "B": (4.0, 0.0),
        "C": (1.2, 1.45), "D": (2.8, 1.45),
    }
    members = [
        ("A", "B", "AB — bottom chord"),
        ("A", "C", "AC — diagonal"),
        ("B", "C", "BC — diagonal"),
        ("A", "D", "AD — diagonal"),
        ("B", "D", "BD — diagonal"),
        ("C", "D", "CD — added redundant member"),
    ]
    fig = go.Figure()
    for start, end, label in members:
        added = (start, end) == ("C", "D")
        _add_member(
            fig, nodes, start, end, label,
            color="#dc2626" if added else "#1e3a5f",
            width=5.0 if added else 3.0,
        )
    _add_supports(fig, nodes, ("A", "B"))
    _add_nodes(fig, nodes)
    _add_force_arrow(fig, (1.2, 2.18), (1.2, 1.70), "P₁",
                     label_position=(1.42, 2.00))
    _add_force_arrow(fig, (2.8, 2.18), (2.8, 1.70), "P₂",
                     label_position=(3.02, 2.00))
    fig.add_annotation(
        x=2.0, y=0.93, text="<b>CD: added load path</b>",
        showarrow=False, font={"size": 10, "color": "#b91c1c"},
        bgcolor="#fff1f2", bordercolor="#fda4af", borderpad=3,
    )
    return _layout(
        fig, "Optimization topology — added member CD in red", height=415,
        x_range=(-0.7, 4.7), y_range=(-0.8, 2.55),
    )


def make_topic_figure(index: int) -> go.Figure:
    """Build the interactive Plotly diagram for a tutorial index."""
    builders = (_basic_figure, _types_figure, _joints_figure,
                _sections_figure, _determinacy_figure, _optimization_figure)
    return builders[index]() if 0 <= index < len(builders) else _basic_figure()


def _render_formula_cards(title: str) -> None:
    for index, (label, formula) in enumerate(FORMULAS.get(title, [])):
        with st.container(key=f"learn_formula_{index}"):
            st.markdown(f'<div class="learn-formula-label">{label}</div>',
                        unsafe_allow_html=True)
            st.latex(formula)


def _render_assumptions() -> None:
    with st.expander("Ideal truss assumptions", expanded=False):
        st.markdown("\n".join(f"- {item}" for item in ASSUMPTIONS))


def render_learn(
    *,
    tutorials: Sequence[Tutorial],
    current_index: int,
    completed_indices: Sequence[int],
    on_mark_read: IndexCallback,
    on_navigate: IndexCallback,
    extra_renderer: OptionalRenderer | None = None,
) -> None:
    """Render Learn; callbacks keep XP, persistence, and routing in the parent app."""
    if not tutorials:
        st.info("Tutorial content is not available yet.")
        return

    index = max(0, min(int(current_index), len(tutorials) - 1))
    titles = [str(item.get("title", f"Topic {n + 1}"))
              for n, item in enumerate(tutorials)]

    with st.container(key="learn_page"):
        st.markdown(LEARN_CSS, unsafe_allow_html=True)
        st.markdown('<div class="learn-eyebrow">Learn by exploring</div>',
                    unsafe_allow_html=True)
        st.title("📖 Interactive Tutorials")
        st.markdown(
            '<div class="learn-intro">Explore structural engineering with interactive '
            'diagrams, clear formulas, and step-by-step explanations. Hover over '
            'joints and members to inspect the model.</div>',
            unsafe_allow_html=True,
        )

        def _select_topic_changed() -> None:
            """Route selector changes through the same parent-owned callback."""
            selected_title = st.session_state.get("learn_topic_selector")
            if selected_title in titles:
                on_navigate(titles.index(selected_title))

        selected = st.selectbox(
            "Choose a topic",
            titles,
            index=index,
            key="learn_topic_selector",
            on_change=_select_topic_changed,
        )
        # Read the widget's current value; button callbacks synchronize this key
        # before Streamlit reruns, so selection and displayed content cannot diverge.
        index = titles.index(selected)

        tutorial = tutorials[index]
        title = titles[index]
        is_complete = index in set(completed_indices)

        title_col, status_col = st.columns([3, 1], gap="small")
        with title_col:
            st.subheader(f"{index + 1}. {title}")
            st.caption(f"Topic {index + 1} of {len(tutorials)}")
        with status_col:
            st.success("✅ Completed") if is_complete else st.info("⭐ +15 XP")

        theory_col, visual_col = st.columns([1, 1.15], gap="large")
        with theory_col:
            with st.container(key="learn_theory_panel"):
                st.markdown("#### 📘 Theory")
                st.markdown(_clean_content(str(tutorial.get("content", ""))))
                _render_formula_cards(title)
                if index == 0:
                    st.info(
                        "**Key properties**\n\n"
                        "- Straight, pin-connected members primarily carry axial force.\n"
                        "- Member forces are classified as tension or compression.\n"
                        "- Ideal external loads are applied at joints.\n"
                        "- Triangulated geometry is stable only with suitable connectivity and supports."
                    )
                _render_assumptions()

        with visual_col:
            with st.container(key="learn_visual_panel"):
                st.markdown("#### 🧭 Interactive visualization")
                fig = make_topic_figure(index)
                st.plotly_chart(
                    fig, use_container_width=True,
                    config={"responsive": True, "displaylogo": False, "scrollZoom": False},
                    key=f"learn_plot_{index}",
                )
                st.markdown(
                    '<div class="learn-muted">Hover over a joint for its x/y coordinates '
                    'or over a member for its structural label.</div>',
                    unsafe_allow_html=True,
                )

        # Keep the existing optimization activity inside the sixth tutorial.
        if index == 5 and extra_renderer is not None:
            st.divider()
            extra_renderer()

        st.divider()
        previous_col, complete_col, next_col = st.columns([1, 1.6, 1], gap="small")
        with previous_col:
            st.button(
                "← Previous",
                disabled=index == 0,
                use_container_width=True,
                key="learn_previous",
                on_click=on_navigate if index > 0 else None,
                args=(index - 1,) if index > 0 else (),
            )
        with complete_col:
            if is_complete:
                st.button("✅ Topic completed", disabled=True, use_container_width=True,
                          key=f"learn_completed_{index}")
            elif st.button("📖 Mark as read (+15 XP)", type="primary",
                           use_container_width=True, key=f"learn_mark_{index}"):
                on_mark_read(index)
        with next_col:
            st.button(
                "Next →",
                disabled=index >= len(tutorials) - 1,
                use_container_width=True,
                key="learn_next",
                on_click=on_navigate if index < len(tutorials) - 1 else None,
                args=(index + 1,) if index < len(tutorials) - 1 else (),
            )
