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
    "Determinate Truss: Force, Stress and Displacement": [
        ("Planar truss determinacy", r"m+r=2j"),
        ("Normal stress", r"\sigma_i=\frac{N_i}{A_i}"),
        ("Axial deformation", r"\delta_i=\frac{N_iL_i}{EA_i}"),
        ("Axial stiffness", r"k_i=\frac{EA_i}{L_i}"),
        ("AB stress example", r"\sigma_{AB}=\frac{20000}{A_{AB}}\ \mathrm{MPa}"),
        ("Vertical displacement result in the notes", r"\delta_{Cv}=\frac{75}{A_{AC}}\ \mathrm{mm}"),
    ],
    "Indeterminate Triangle: Redundant Reaction": [
        ("Degree of indeterminacy", r"D_s=m+r-2j=3+4-6=1"),
        ("Equilibrium: AB", r"N_{AB}=20+R"),
        ("Equilibrium: AC", r"N_{AC}=0.75R-5"),
        ("Equilibrium: BC", r"N_{BC}=-1.25(20+R)"),
        ("Compatibility at C", r"u_C=\sum_i\frac{N_in_iL_i}{EA_i}=0"),
        ("Redundant reaction for the uploaded example", r"R=-\frac{80000/A_1-11250/A_2+156250/A_3}{4000/A_1+1687.5/A_2+7812.5/A_3}"),
    ],
    "Internal Redundancy: Force Method": [
        ("Degree of indeterminacy", r"D_s=m+r-2j=6+3-8=1"),
        ("Chosen redundant", r"X=N_{BD}"),
        ("Force recovery", r"N_i=N_i^{(0)}+Xn_i"),
        ("Member flexibility", r"f_i=\frac{L_i}{EA_i}"),
        ("Compatibility expression in the notes", r"\sum_i\frac{N_in_iL_i}{EA_i}=0"),
        ("Optimization design variables", r"\mathbf{A}=[A_1,A_2,\ldots,A_m]"),
    ],
    "Parallel Bars: Compatibility and Load Sharing": [
        ("Equilibrium", r"F_1+F_2=P"),
        ("Compatibility of plate displacement", r"\delta_1=\delta_2"),
        ("Axial bar deformation", r"\delta_i=\frac{F_iL_i}{E_iA_i}"),
        ("Axial stiffness", r"k_i=\frac{E_iA_i}{L_i}"),
        ("Load-sharing ratio", r"\frac{F_1}{F_2}=\frac{k_1}{k_2}"),
        ("Equal E and equal L", r"\frac{F_1}{F_2}=\frac{A_1}{A_2}"),
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

/* Theory text uses semantic emphasis rather than a single flat text style. */
.st-key-learn_theory_panel .learn-concept {
  color:#0369a1; font-weight:800;
}
.st-key-learn_theory_panel mark.learn-highlight {
  color:#713f12; background:#fef08a; font-weight:750;
  padding:.06rem .22rem; border-radius:.25rem;
  border-bottom:2px solid #f59e0b;
}
.st-key-learn_theory_panel .learn-positive {
  color:#166534; background:#dcfce7; font-weight:750;
  padding:.04rem .2rem; border-radius:.25rem;
}
.st-key-learn_theory_panel .learn-warning {
  color:#991b1b; background:#fee2e2; font-weight:750;
  padding:.04rem .2rem; border-radius:.25rem;
}
.st-key-learn_theory_panel .learn-equation {
  color:#1d4ed8; background:#eff6ff; font-weight:800;
  padding:.06rem .24rem; border-radius:.3rem; white-space:normal;
}
.st-key-learn_theory_panel h4 {
  color:#164e63; background:#ecfeff;
  border-left:4px solid #0891b2; border-radius:0 8px 8px 0;
  padding:.42rem .62rem; margin:1.05rem 0 .55rem;
  font-size:1rem; line-height:1.4;
}
.st-key-learn_theory_panel [data-testid="stMarkdownContainer"] ul,
.st-key-learn_theory_panel [data-testid="stMarkdownContainer"] ol {
  padding-left:1.35rem; margin-top:.28rem; margin-bottom:.65rem;
}
.st-key-learn_theory_panel [data-testid="stMarkdownContainer"] li {
  padding-left:.12rem; margin-bottom:.32rem; line-height:1.58;
}
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
    """Turn legacy tutorial markup into accessible, semantically highlighted Markdown."""
    # Legacy tags carry meaning: cyan = concept, yellow = highlight, green = positive,
    # red = warning/compression, and bold = a short emphasis or subsection label.
    styled_patterns = (
        (r"\[bold\s+cyan\](.*?)\[/bold\s+cyan\]", '<span class="learn-concept">', "</span>"),
        (r"\[yellow\](.*?)\[/yellow\]", '<mark class="learn-highlight">', "</mark>"),
        (r"\[green\](.*?)\[/green\]", '<span class="learn-positive">', "</span>"),
        (r"\[red\](.*?)\[/red\]", '<span class="learn-warning">', "</span>"),
        (r"\[bold\](.*?)\[/bold\]", "**", "**"),
    )
    for pattern, opening, closing in styled_patterns:
        text = re.sub(
            pattern,
            lambda match, start=opening, finish=closing:
                f"{start}{match.group(1)}{finish}",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

    # Remove any unrecognized legacy markup without touching the HTML added above.
    text = re.sub(r"\[/?[^\]]+\]", "", text).strip()

    # Keep the example mathematically readable while removing the old terminal glyphs.
    text = re.sub(
        r"Example: A simple triangular truss with pin \+ roller support:\s*"
        r"m = 3, r = 3, j = 3\s*→\s*3 \+ 3 = 2\(3\) = 6\s*✓ Determinate",
        "Example: A simple triangular truss with pin and roller support has "
        "m = 3, r = 3 and j = 3. Hence m + r = 2j = 6: determinate by count.",
        text,
        flags=re.IGNORECASE,
    )

    # Highlight equations and checks wherever they occur in the explanation.
    equation_pattern = (
        r"(?<![A-Za-z])(?:m\s*\+\s*r\s*(?:=|<|>)\s*2j"
        r"|ΣF[xXyY]\s*=\s*0|ΣM\s*=\s*0"
        r"|V\s*=\s*Σ\(Lᵢ\s*Aᵢ\)|EA\s*/\s*L)"
    )

    def _equation_span(match: re.Match[str]) -> str:
        equation = match.group(0).replace("<", "&lt;").replace(">", "&gt;")
        return f'<span class="learn-equation">{equation}</span>'

    text = re.sub(equation_pattern, _equation_span, text)

    headings = {
        "key properties": "🔑 Key properties",
        "common uses": "🏗️ Common applications",
        "steps": "🧭 Step-by-step method",
        "tips": "💡 Important tips",
        "when to use it": "🎯 When to use this method",
        "choosing the moment point": "🎯 Choosing the moment point",
        "the determinacy equation": "📐 Determinacy check",
        "determinacy equation": "📐 Determinacy check",
        "geometric instability": "⚠️ Geometric stability",
        "important scope note": "⚠️ Model limitations",
    }

    output: list[str] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            output.append("")
            continue

        # Preserve a small amount of indentation so genuinely nested bullet points
        # remain nested, while avoiding Markdown's four-space code-block behavior.
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        # Recognize both legacy-bold headers and ordinary "Heading:" lines.
        header_candidate = re.sub(r"^\*\*(.*?)\*\*:?$", r"\1", line).strip().rstrip(":")
        header_key = header_candidate.casefold()
        if header_key in headings:
            output.append(f"#### {headings[header_key]}")
            continue

        if line.startswith("• "):
            prefix = "  " if indent >= 4 else ""
            line = f"{prefix}- {line[2:].strip()}"
        elif re.match(r"^-\s+", line):
            prefix = "  " if indent >= 4 else ""
            line = prefix + line
        elif re.match(r"^\d+\.\s+", line):
            prefix = "  " if indent >= 4 else ""
            line = prefix + line

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
    panels = (("Pratt", 0.0), ("Warren", 4.35), ("Howe", 8.70))

    def add_chord(nodes: Mapping[str, tuple[float, float]], names: Sequence[str],
                  label: str, color: str = "#1e3a5f") -> None:
        for left, right in zip(names, names[1:]):
            _add_member(fig, nodes, left, right, f"{label}: {left}-{right}",
                        color=color, width=2.6)

    for title, offset in panels:
        bottom_points = [(offset + i, 0.0) for i in range(4)]
        if title == "Warren":
            top_points = [(offset + 0.5, 0.55), (offset + 1.5, 0.55),
                          (offset + 2.5, 0.55)]
            nodes = {
                **{name: point for name, point in zip(("A", "B", "C", "D"), bottom_points)},
                **{name: point for name, point in zip(("E", "F", "G"), top_points)},
            }
            add_chord(nodes, ("A", "B", "C", "D"), "Bottom chord")
            diagonals = (
                ("A", "E"), ("E", "B"), ("B", "F"),
                ("F", "C"), ("C", "G"), ("G", "D"),
            )
            for a, b in diagonals:
                _add_member(fig, nodes, a, b, f"Warren diagonal {a}-{b}",
                            color="#d97706", width=2.8)
        else:
            top_points = [(offset + i, 0.55) for i in range(4)]
            nodes = {
                **{name: point for name, point in zip(("A", "B", "C", "D"), bottom_points)},
                **{name: point for name, point in zip(("E", "F", "G", "H"), top_points)},
            }
            add_chord(nodes, ("A", "B", "C", "D"), "Bottom chord")
            add_chord(nodes, ("E", "F", "G", "H"), "Top chord")
            for bottom, top in zip(("A", "B", "C", "D"), ("E", "F", "G", "H")):
                _add_member(fig, nodes, bottom, top, f"Vertical {bottom}-{top}",
                            color="#64748b", width=2.2)
            for i in range(3):
                if title == "Pratt":
                    a, b, diagonal_color = ("E", "F", "G")[i], ("B", "C", "D")[i], "#15803d"
                else:
                    a, b, diagonal_color = ("A", "B", "C")[i], ("F", "G", "H")[i], "#b91c1c"
                _add_member(fig, nodes, a, b, f"{title} diagonal {a}-{b}",
                            color=diagonal_color, width=2.8)
        _add_supports(fig, nodes, ("A", "D"))
        _add_nodes(fig, nodes)
        fig.add_annotation(
            x=offset + 1.5, y=1.13, text=f"<b>{title} truss</b>",
            showarrow=False, font={"size": 12, "color": "#1d4ed8"},
        )
        note = {
            "Pratt": "Diagonals: green",
            "Warren": "Alternating triangular web",
            "Howe": "Diagonals slope opposite Pratt",
        }[title]
        fig.add_annotation(
            x=offset + 1.5, y=-0.66, text=note, showarrow=False,
            font={"size": 9, "color": "#475569"},
        )
    return _layout(
        fig, "Compare common planar truss configurations", height=365,
        x_range=(-0.55, 12.95), y_range=(-0.84, 1.38), equal_scale=False,
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
    """Topic 5: compare determinate, redundant and unstable four-joint trusses."""
    fig = go.Figure()
    cases = [
        (0.0, "DETERMINATE", "#15803d", "m=5, r=3, j=4", "m+r=2j (8=8)"),
        (3.0, "INDETERMINATE", "#b45309", "m=6, r=3, j=4", "m+r>2j (9>8)"),
        (6.0, "UNSTABLE", "#b91c1c", "m=4, r=3, j=4", "m+r<2j (7<8)"),
    ]
    for offset, title, color, subtitle, formula in cases:
        nodes = {
            "A": (offset, 0.0), "B": (offset + 2.0, 0.0),
            "C": (offset + 2.0, 0.45), "D": (offset, 0.45),
        }
        for start, end, label in (
            ("A", "B", "Bottom chord"), ("B", "C", "Right vertical"),
            ("C", "D", "Top chord"), ("D", "A", "Left vertical"),
        ):
            _add_member(fig, nodes, start, end, f"{title}: {label}", width=2.7)
        if title != "UNSTABLE":
            _add_member(fig, nodes, "A", "C", f"{title}: diagonal AC",
                        color=color, width=3.3)
        if title == "INDETERMINATE":
            _add_member(fig, nodes, "B", "D", "Redundant diagonal BD",
                        color="#d97706", width=3.3)
        _add_supports(fig, nodes, ("A", "B"))
        _add_nodes(fig, nodes)
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
        x=2.0, y=1.64, text="<b>CD — added member</b>",
        showarrow=False, font={"size": 10, "color": "#b91c1c"},
        bgcolor="#fff1f2", bordercolor="#fda4af", borderpad=2,
    )
    return _layout(
        fig, "Optimization topology — added member CD in red", height=415,
        x_range=(-0.7, 4.7), y_range=(-0.8, 2.55),
    )



def _determinate_example_figure() -> go.Figure:
    """Uploaded notes: 3-4-5 determinate triangle with two loads at C."""
    nodes = {"A": (0.0, 0.0), "B": (4.0, 0.0), "C": (0.0, 3.0)}
    fig = go.Figure()
    for a, b, label in (
        ("A", "B", "AB — 4 m bottom member"),
        ("A", "C", "AC — 3 m vertical member"),
        ("B", "C", "BC — 5 m diagonal"),
    ):
        _add_member(fig, nodes, a, b, label, width=4.0)
    _add_supports(fig, nodes, ("A", "B"))
    _add_nodes(fig, nodes)
    _add_force_arrow(fig, (-0.9, 3.0), (0.0, 3.0), "Px = 20 kN",
                     label_position=(-0.52, 3.23), color="#92400e")
    _add_force_arrow(fig, (0.0, 4.05), (0.0, 3.15), "Py = 20 kN",
                     label_position=(0.48, 3.78), color="#92400e")
    _add_force_arrow(fig, (0.0, 0.0), (-0.82, 0.0), "Ax = −20 kN",
                     label_position=(-0.57, 0.24), color="#6d28d9")
    _add_force_arrow(fig, (0.0, 0.0), (0.0, 0.62), "Ay = 5 kN",
                     label_position=(0.48, 0.43), color="#6d28d9")
    _add_force_arrow(fig, (4.0, 0.0), (4.0, 0.62), "By = 15 kN",
                     label_position=(4.68, 0.43), color="#6d28d9")
    _add_dimension(fig, 0.0, 4.0, -0.66, "4 m")
    fig.add_annotation(x=0.5, y=1.58, text="AB: 20 kN tension",
                       showarrow=False, font={"size": 10, "color": "#166534"},
                       bgcolor="#dcfce7", borderpad=3)
    fig.add_annotation(x=0.53, y=2.25, text="AC: 5 kN compression",
                       showarrow=False, font={"size": 10, "color": "#991b1b"},
                       bgcolor="#fee2e2", borderpad=3)
    fig.add_annotation(x=2.65, y=1.30, text="BC: 25 kN compression",
                       showarrow=False, font={"size": 10, "color": "#991b1b"},
                       bgcolor="#fee2e2", borderpad=3)
    return _layout(
        fig, "Determinate 3–4–5 truss — reactions and member forces",
        height=430, x_range=(-1.35, 5.05), y_range=(-0.95, 4.4), equal_scale=False,
    )


def _indeterminate_triangle_figure() -> go.Figure:
    """Uploaded notes: the triangular truss gains a horizontal reaction at C."""
    nodes = {"A": (0.0, 0.0), "B": (4.0, 0.0), "C": (0.0, 3.0)}
    fig = go.Figure()
    for a, b, label in (
        ("A", "B", "AB — 4 m"),
        ("A", "C", "AC — 3 m"),
        ("B", "C", "BC — 5 m"),
    ):
        _add_member(fig, nodes, a, b, label, width=4.0)
    _add_supports(fig, nodes, ("A", "B"))
    _add_nodes(fig, nodes)
    # The vertical guide and small rollers indicate the added horizontal restraint at C.
    fig.add_shape(type="line", x0=-0.32, y0=2.45, x1=-0.32, y1=3.60,
                  line={"color": "#475569", "width": 3})
    for yy in (2.73, 3.14):
        fig.add_shape(type="circle", x0=-0.22, x1=-0.10, y0=yy-0.06, y1=yy+0.06,
                      line={"color": "#475569", "width": 1.5}, fillcolor="#e2e8f0")
    fig.add_annotation(x=-0.58, y=3.65, text="Vertical guide",
                       showarrow=False, font={"size": 9, "color": "#475569"})
    _add_force_arrow(fig, (0.0, 3.36), (0.85, 3.36), "Px = 20 kN",
                     label_position=(0.48, 3.61), color="#92400e")
    _add_force_arrow(fig, (0.30, 4.05), (0.30, 3.18), "Py = 20 kN",
                     label_position=(0.73, 3.93), color="#92400e")
    _add_force_arrow(fig, (0.0, 2.75), (-0.78, 2.75), "R = Cx",
                     label_position=(-0.53, 2.98), color="#6d28d9")
    _add_force_arrow(fig, (0.0, 0.0), (-0.68, 0.0), "Ax",
                     label_position=(-0.48, 0.22), color="#6d28d9")
    _add_force_arrow(fig, (0.0, 0.0), (0.0, 0.52), "Ay",
                     label_position=(0.20, 0.40), color="#6d28d9")
    _add_force_arrow(fig, (4.0, 0.0), (4.0, 0.52), "By",
                     label_position=(4.20, 0.40), color="#6d28d9")
    fig.add_annotation(
        x=2.0, y=1.0, text="<b>m = 3, r = 4, j = 3</b><br>m + r − 2j = 1",
        showarrow=False, font={"size": 11, "color": "#92400e"},
        bgcolor="#fffbeb", bordercolor="#f59e0b", borderpad=5,
    )
    return _layout(
        fig, "One extra reaction — choose R = Cx as the redundant",
        height=430, x_range=(-1.15, 5.0), y_range=(-0.82, 4.35), equal_scale=False,
    )


def _double_diagonal_figure() -> go.Figure:
    """Uploaded notes: rectangular truss with both diagonals, BD as redundant."""
    nodes = {
        "A": (0.0, 0.0), "B": (4.0, 0.0),
        "C": (4.0, 3.0), "D": (0.0, 3.0),
    }
    members = (
        ("A", "B", "AB — bottom chord"),
        ("B", "C", "BC — right vertical"),
        ("C", "D", "CD — top chord"),
        ("D", "A", "DA — left vertical"),
        ("A", "C", "AC — primary diagonal"),
        ("B", "D", "BD — selected redundant"),
    )
    fig = go.Figure()
    for a, b, label in members:
        redundant = (a, b) == ("B", "D")
        _add_member(
            fig, nodes, a, b, label,
            color="#dc2626" if redundant else "#1e3a5f",
            width=5.0 if redundant else 3.2,
            dash="dash" if redundant else "solid",
        )
    _add_supports(fig, nodes, ("A", "B"))
    _add_nodes(fig, nodes)
    _add_force_arrow(fig, (4.0, 4.05), (4.0, 3.12), "P = 10 kN",
                     label_position=(4.58, 3.70), color="#92400e")
    _add_force_arrow(fig, (0.0, 0.0), (0.0, 0.56), "Ay",
                     label_position=(0.25, 0.40), color="#6d28d9")
    _add_force_arrow(fig, (4.0, 0.0), (4.0, 0.56), "By",
                     label_position=(4.26, 0.40), color="#6d28d9")
    _add_dimension(fig, 0.0, 4.0, -0.66, "4 m")
    fig.add_annotation(
        x=2.0, y=1.85, text="<b>BD is removed to form the primary structure</b>",
        showarrow=False, font={"size": 10, "color": "#991b1b"},
        bgcolor="#fff1f2", bordercolor="#fda4af", borderpad=4,
    )
    fig.add_annotation(
        x=2.55, y=2.65, text="AC retained",
        showarrow=False, font={"size": 9, "color": "#1e3a5f"},
        bgcolor="#eff6ff", borderpad=2,
    )
    return _layout(
        fig, "Internally indeterminate rectangular truss", height=430,
        x_range=(-0.8, 5.05), y_range=(-1.0, 4.45), equal_scale=False,
    )


def _small_indeterminate_response(
    areas_mm2: Sequence[float],
) -> dict[str, float]:
    """Solve the area-dependent redundant reaction using the uploaded notes' equation."""
    if len(areas_mm2) != 3:
        raise ValueError("Provide areas for AB, AC and BC.")
    a1, a2, a3 = (float(value) for value in areas_mm2)
    if any(not (500.0 <= area <= 10000.0) for area in (a1, a2, a3)):
        raise ValueError("Areas must lie in the demonstrator range 500–10000 mm².")
    numerator = 80000.0 / a1 - 11250.0 / a2 + 156250.0 / a3
    denominator = 4000.0 / a1 + 1687.5 / a2 + 7812.5 / a3
    if denominator <= 0:
        raise ValueError("The flexibility denominator must be positive.")
    reaction = -numerator / denominator
    return {
        "R": reaction,
        "N_AB": 20.0 + reaction,
        "N_AC": 0.75 * reaction - 5.0,
        "N_BC": -1.25 * (20.0 + reaction),
    }


def _render_determinate_area_demo() -> None:
    st.markdown("#### 🧪 Try it: area changes stress, not ideal determinate force")
    area = st.slider(
        "Area of member AB (mm²)", min_value=500, max_value=2000,
        value=1000, step=100, key="learn_determinate_ab_area",
    )
    force_kn = 20.0
    stress_mpa = force_kn * 1000.0 / area
    c1, c2 = st.columns(2)
    with c1:
        st.metric("AB member force", f"{force_kn:.1f} kN", "fixed by equilibrium")
    with c2:
        st.metric("AB normal stress", f"{stress_mpa:.1f} MPa")
    st.caption(
        "Using N_AB = 20 kN from the uploaded example. "
        "Stress is calculated as N/A, with 1 MPa = 1 N/mm²."
    )
    fig = go.Figure(go.Bar(
        x=["A = 1000 mm²", f"A = {area} mm²"],
        y=[20.0, stress_mpa],
        marker_color=["#2563eb", "#d97706"],
        text=[f"{20.0:.1f} MPa", f"{stress_mpa:.1f} MPa"],
        textposition="outside",
        hovertemplate="%{x}<br>Stress = %{y:.2f} MPa<extra></extra>",
    ))
    fig.update_layout(
        title="Area controls stress for this fixed member force",
        yaxis_title="Normal stress (MPa)", height=300,
        margin={"l": 10, "r": 10, "t": 55, "b": 20},
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})


def _render_indeterminate_area_lab() -> None:
    st.markdown("#### 🧪 Glass-box experiment: change areas and watch the forces redistribute")
    st.caption(
        "This reproduces the reaction equation from the uploaded three-member example. "
        "A1 = AB, A2 = AC, and A3 = BC. All areas are in mm²; forces and R are in kN."
    )
    columns = st.columns(3)
    labels = ("A1 — AB (mm²)", "A2 — AC (mm²)", "A3 — BC (mm²)")
    keys = ("learn_ind_A1", "learn_ind_A2", "learn_ind_A3")
    values: list[int] = []
    for col, label, key in zip(columns, labels, keys):
        with col:
            values.append(st.slider(
                label, min_value=500, max_value=4000, step=500,
                value=1000, key=key,
            ))
    response = _small_indeterminate_response(values)
    st.metric("Redundant reaction R = Cx", f"{response['R']:.3f} kN")
    records = []
    for member in ("N_AB", "N_AC", "N_BC"):
        force = response[member]
        records.append({
            "Member": member.replace("N_", ""),
            "Area (mm²)": values[("N_AB", "N_AC", "N_BC").index(member)],
            "Force (kN)": round(force, 3),
            "Nature": "Tension" if force > 1e-8 else "Compression" if force < -1e-8 else "Zero",
        })
    st.dataframe(records, use_container_width=True, hide_index=True)
    colours = [
        "#15803d" if item["Force (kN)"] >= 0 else "#b91c1c"
        for item in records
    ]
    fig = go.Figure(go.Bar(
        x=[item["Member"] for item in records],
        y=[item["Force (kN)"] for item in records],
        marker_color=colours,
        text=[f"{item['Force (kN)']:.3f}" for item in records],
        textposition="outside",
        hovertemplate="%{x}<br>Signed axial force = %{y:.3f} kN<extra></extra>",
    ))
    fig.update_layout(
        title="Signed member forces (positive = tension, negative = compression)",
        yaxis_title="Force (kN)", height=330,
        margin={"l": 10, "r": 10, "t": 55, "b": 20},
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.info(
        "Compare the default equal-area case (R ≈ −16.667 kN) with A3 = 2000 mm² "
        "(R ≈ −15.309 kN). A change in one area changes the redundant reaction and "
        "the forces in all three members."
    )


def _render_force_method_audit() -> None:
    st.markdown("#### 🔎 Glass-box force-method audit")
    st.caption(
        "The study note gives the following virtual-force magnitudes and member lengths. "
        "This panel checks the displayed denominator terms, rather than silently accepting the printed result."
    )
    terms = [
        ("AB", 0.8 ** 2 * 4000),
        ("BC", 0.6 ** 2 * 3000),
        ("CD", 0.8 ** 2 * 4000),
        ("DA", 0.6 ** 2 * 3000),
        ("AC", 1.0 ** 2 * 5000),
    ]
    denominator_sum = sum(value for _, value in terms)
    st.dataframe(
        [{"Primary member": name, "n²L term (mm)": f"{value:.0f}"}
         for name, value in terms]
        + [{"Primary member": "Sum of listed terms",
            "n²L term (mm)": f"{denominator_sum:.0f}"}],
        use_container_width=True, hide_index=True,
    )
    st.warning(
        f"The displayed terms sum to {denominator_sum:.0f} mm, not the 13,400 mm "
        "denominator reported in the PDF. The PDF also abbreviates the compatibility "
        "condition as δBD = 0. Verify the redundant-member compatibility convention "
        "and the numerical solution with the instructor before treating its reported "
        "X = −1.3433 kN as a validated answer."
    )



def _parallel_bars_figure() -> go.Figure:
    """Two axial bars under a rigid plate, illustrating compatible load sharing."""
    nodes = {
        "A": (0.0, 0.0), "B": (3.0, 0.0),
        "C": (0.0, 2.0), "D": (3.0, 2.0),
    }
    fig = go.Figure()
    _add_member(fig, nodes, "A", "C", "Bar 1 — area A1", color="#2563eb", width=7.0)
    _add_member(fig, nodes, "B", "D", "Bar 2 — area A2", color="#d97706", width=7.0)
    _add_member(fig, nodes, "C", "D", "Rigid plate — compatible top movement",
                color="#334155", width=9.0)
    _add_supports(fig, nodes, ("A", "B"))
    _add_nodes(fig, nodes)
    _add_force_arrow(fig, (0.0, 2.0), (0.0, 2.72), "F1",
                     label_position=(-0.28, 2.50), color="#2563eb")
    _add_force_arrow(fig, (3.0, 2.0), (3.0, 2.72), "F2",
                     label_position=(3.27, 2.50), color="#d97706")
    _add_force_arrow(fig, (1.5, 3.55), (1.5, 2.28), "P = 100 kN",
                     label_position=(1.95, 3.18), color="#92400e")
    fig.add_annotation(
        x=0.0, y=1.10, text="<b>A1</b>", showarrow=False,
        font={"size": 12, "color": "#1d4ed8"},
        bgcolor="#eff6ff", borderpad=3,
    )
    fig.add_annotation(
        x=3.0, y=1.10, text="<b>A2</b>", showarrow=False,
        font={"size": 12, "color": "#92400e"},
        bgcolor="#fffbeb", borderpad=3,
    )
    fig.add_annotation(
        x=1.5, y=1.55, text="Rigid plate: δ1 = δ2",
        showarrow=False, font={"size": 10, "color": "#334155"},
        bgcolor="#f1f5f9", borderpad=3,
    )
    return _layout(
        fig, "Parallel-bar system — equilibrium plus compatibility",
        height=405, x_range=(-0.8, 3.8), y_range=(-0.8, 4.0), equal_scale=False,
    )


def _render_parallel_bar_lab() -> None:
    st.markdown("#### 🧪 Interactive experiment: see stiffness share the load")
    st.caption(
        "Source setup: P = 100 kN, equal material and equal bar length. "
        "Change the areas and compare the two axial forces."
    )
    a1_col, a2_col = st.columns(2)
    with a1_col:
        area1 = st.slider(
            "Bar 1 area A1 (mm²)", 500, 4000, 1000, step=500,
            key="learn_parallel_area_1",
        )
    with a2_col:
        area2 = st.slider(
            "Bar 2 area A2 (mm²)", 500, 4000, 2000, step=500,
            key="learn_parallel_area_2",
        )
    total_area = float(area1 + area2)
    force1 = 100.0 * area1 / total_area
    force2 = 100.0 * area2 / total_area
    left, right = st.columns(2)
    with left:
        st.metric("Force in bar 1", f"{force1:.2f} kN")
    with right:
        st.metric("Force in bar 2", f"{force2:.2f} kN")
    st.success(f"Equilibrium check: F1 + F2 = {force1 + force2:.2f} kN = P")
    st.markdown(
        f"**Stiffness ratio:** k1/k2 = A1/A2 = {area1}/{area2} = "
        f"{area1 / area2:.3f}. Because the material and lengths are equal, "
        "the axial-force ratio equals the area ratio."
    )
    fig = go.Figure(go.Bar(
        x=["Bar 1", "Bar 2"], y=[force1, force2],
        marker_color=["#2563eb", "#d97706"],
        text=[f"{force1:.2f} kN", f"{force2:.2f} kN"],
        textposition="outside",
        hovertemplate="%{x}<br>Force = %{y:.2f} kN<extra></extra>",
    ))
    fig.update_layout(
        title="Load shared by each bar", yaxis_title="Axial force (kN)",
        height=300, margin={"l": 10, "r": 10, "t": 55, "b": 20},
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.info(
        "Try A1 = 1000 mm² with A2 = 2000 mm² (about 33.33 / 66.67 kN), "
        "then raise A2 to 4000 mm² (20 / 80 kN), as in the uploaded notes."
    )


def make_topic_figure(index: int) -> go.Figure:
    """Build the interactive Plotly diagram for a tutorial index."""
    builders = (
        _basic_figure,
        _types_figure,
        _joints_figure,
        _sections_figure,
        _determinacy_figure,
        _optimization_figure,
        _determinate_example_figure,
        _indeterminate_triangle_figure,
        _double_diagonal_figure,
        _parallel_bars_figure,
    )
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
                # Content is sourced from the app's authored tutorial bank; semantic
                # emphasis tags are generated by _clean_content and styled by LEARN_CSS.
                st.markdown(
                    _clean_content(str(tutorial.get("content", ""))),
                    unsafe_allow_html=True,
                )
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
                if index == 2:
                    # The joint-level free-body diagram complements the full truss
                    # without squeezing both drawings into one small plotting area.
                    st.plotly_chart(
                        _joints_fbd_figure(),
                        use_container_width=True,
                        config={"responsive": True, "displaylogo": False, "scrollZoom": False},
                        key="learn_joint_fbd",
                    )
                st.markdown(
                    '<div class="learn-muted">Hover over a joint for its x/y coordinates '
                    'or over a member for its structural label. Loads, reactions, '
                    'supports and highlighted members are shown where relevant.</div>',
                    unsafe_allow_html=True,
                )

        # Keep the existing optimization activity inside the sixth tutorial.
        if index == 5 and extra_renderer is not None:
            st.divider()
            extra_renderer()

        # Additional experiments are based on the three uploaded study notes.
        if index == 6:
            st.divider()
            _render_determinate_area_demo()
        elif index == 7:
            st.divider()
            _render_indeterminate_area_lab()
        elif index == 8:
            st.divider()
            _render_force_method_audit()
        elif index == 9:
            st.divider()
            _render_parallel_bar_lab()

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
