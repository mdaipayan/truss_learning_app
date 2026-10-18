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


def _add_nodes(fig: go.Figure, nodes: Mapping[str, tuple[float, float]],
               highlight: str | None = None) -> None:
    names = list(nodes)
    fig.add_trace(go.Scatter(
        x=[nodes[name][0] for name in names],
        y=[nodes[name][1] for name in names],
        mode="markers+text", text=names, textposition="top center",
        marker={
            "size": [14 if name == highlight else 10 for name in names],
            "color": ["#f59e0b" if name == highlight else "#2563eb" for name in names],
            "line": {"color": "#ffffff", "width": 1.5},
        },
        customdata=[[name, nodes[name][0], nodes[name][1]] for name in names],
        hovertemplate=(
            "<b>Joint %{customdata[0]}</b><br>"
            "x = %{customdata[1]:.2f} m<br>"
            "y = %{customdata[2]:.2f} m<extra></extra>"
        ),
        showlegend=False,
    ))


def _layout(fig: go.Figure, title: str, *, height: int = 370) -> go.Figure:
    fig.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left"},
        autosize=True, height=height,
        margin={"l": 20, "r": 20, "t": 48, "b": 24},
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font={"family": "Inter, Arial, sans-serif", "size": 12, "color": "#0f172a"},
        hoverlabel={"bgcolor": "#ffffff", "font_size": 13},
        showlegend=False,
    )
    fig.update_xaxes(title="x (m)", showgrid=True, gridcolor="#eef2f7",
                     zeroline=False, automargin=True)
    fig.update_yaxes(title="y (m)", showgrid=True, gridcolor="#eef2f7",
                     zeroline=False, automargin=True, scaleanchor="x", scaleratio=1)
    return fig


def _basic_figure() -> go.Figure:
    """Topic 1: a triangular roof truss with node-coordinate and member hover."""
    fig = go.Figure()
    for start, end, label in BASIC_MEMBERS:
        _add_member(fig, BASIC_NODES, start, end, label)
    _add_nodes(fig, BASIC_NODES)
    fig.add_annotation(
        x=2, y=-0.25, text="4.0 m span", showarrow=False,
        font={"size": 11, "color": "#64748b"},
    )
    fig.add_annotation(
        x=2.0, y=1.65, ax=2.0, ay=2.1, axref="x", ayref="y",
        text="Roof apex C", showarrow=True, arrowhead=2,
        arrowcolor="#b45309", font={"size": 10, "color": "#92400e"},
    )
    return _layout(fig, "Explore a simple triangular roof truss")


def _types_figure() -> go.Figure:
    """Topic 2: hoverable Pratt, Warren and Howe schematic topologies on one plot."""
    fig = go.Figure()
    schemes = [
        ("Pratt", 0.0, [(0,0),(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1)],
         [(0,1),(1,2),(2,3),(4,5),(5,6),(6,7),(0,4),(1,5),(2,6),(3,7),(0,5),(2,7)]),
        ("Warren", 4.4, [(0,0),(1,0),(2,0),(3,0),(.5,1),(1.5,1),(2.5,1)],
         [(0,1),(1,2),(2,3),(0,4),(4,1),(1,5),(5,2),(2,6),(6,3)]),
        ("Howe", 8.8, [(0,0),(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1)],
         [(0,1),(1,2),(2,3),(4,5),(5,6),(6,7),(0,4),(1,5),(2,6),(3,7),(1,4),(3,6)]),
    ]
    for title, x_offset, points, members in schemes:
        names = [f"{title[0]}{i+1}" for i in range(len(points))]
        nodes = {name: (x + x_offset, y) for name, (x, y) in zip(names, points)}
        for i, j in members:
            _add_member(fig, nodes, names[i], names[j],
                        f"{title} member {names[i]}–{names[j]}", width=2.4)
        _add_nodes(fig, nodes)
        fig.add_annotation(x=x_offset + 1.5, y=1.35, text=f"<b>{title}</b>",
                           showarrow=False, font={"size": 12, "color": "#1d4ed8"})
    fig.update_layout(
        title={"text": "Compare common planar truss layouts", "x": 0.02},
        autosize=True, height=330, margin={"l": 10, "r": 10, "t": 48, "b": 10},
        paper_bgcolor="#fff", plot_bgcolor="#fff",
        font={"family": "Inter, Arial, sans-serif", "size": 11, "color": "#0f172a"},
        hoverlabel={"bgcolor": "#fff", "font_size": 12}, showlegend=False,
    )
    fig.update_xaxes(visible=False, range=[-0.6, 12.5])
    fig.update_yaxes(visible=False, range=[-0.3, 1.7], scaleanchor="x", scaleratio=0.38)
    return fig


def _joints_figure() -> go.Figure:
    fig = go.Figure()
    for start, end, label in BASIC_MEMBERS:
        _add_member(fig, BASIC_NODES, start, end, label,
                    color="#f59e0b" if "A" in (start, end) else "#1e3a5f",
                    width=4.5)
    _add_nodes(fig, BASIC_NODES, highlight="A")
    fig.add_annotation(
        x=.75, y=.75, ax=0, ay=0, axref="x", ayref="y",
        text="Start at a joint with<br>at most 2 unknowns",
        showarrow=True, arrowhead=2, bgcolor="#fffbeb",
        bordercolor="#f59e0b", borderpad=4,
        font={"size": 10, "color": "#92400e"},
    )
    return _layout(fig, "Method of Joints — start at joint A")


def _sections_figure() -> go.Figure:
    nodes = {"A":(0,0),"B":(1,0),"C":(2,0),"D":(3,0),
             "E":(0,1),"F":(1,1),"G":(2,1),"H":(3,1)}
    members = [
        ("A","B","Bottom chord"),("B","C","Bottom chord"),("C","D","Bottom chord"),
        ("E","F","Top chord"),("F","G","Top chord"),("G","H","Top chord"),
        ("A","E","Vertical"),("B","F","Vertical"),("C","G","Vertical"),("D","H","Vertical"),
        ("A","F","Diagonal"),("B","G","Diagonal"),("C","H","Diagonal"),
    ]
    cut = {("B","C"),("F","G"),("B","G")}
    fig = go.Figure()
    for start, end, label in members:
        is_cut = (start, end) in cut
        _add_member(fig, nodes, start, end, f"{label} {start}{end}",
                    color="#dc2626" if is_cut else "#1e3a5f",
                    width=4.5 if is_cut else 2.4)
    _add_nodes(fig, nodes)
    fig.add_shape(type="line", x0=1.5, y0=-.2, x1=1.5, y1=1.2,
                  line={"color":"#dc2626","width":2,"dash":"dash"})
    fig.add_annotation(x=1.5, y=1.3, text="Section cut", showarrow=False,
                       font={"size":11,"color":"#b91c1c"})
    return _layout(fig, "Method of Sections — isolate a few unknowns")


def _determinacy_figure() -> go.Figure:
    fig = go.Figure()
    for start, end, label in BASIC_MEMBERS:
        _add_member(fig, BASIC_NODES, start, end, label)
    _add_nodes(fig, BASIC_NODES)
    fig.add_annotation(
        x=5.05, y=1.0, text="m = 3 members<br>r = 3 reactions<br>j = 3 joints<br><b>m + r = 2j</b>",
        showarrow=False, align="left", bgcolor="#eff6ff",
        bordercolor="#93c5fd", borderpad=7,
        font={"size":12,"color":"#1e3a8a"},
    )
    fig.update_xaxes(range=[-.5, 6.8])
    return _layout(fig, "Count members, reactions and joints")


def _optimization_figure() -> go.Figure:
    nodes = {"A":(0.0,0.0),"B":(4.0,0.0),"C":(1.2,3.0),"D":(2.8,3.0)}
    members = [
        ("A","B","AB — bottom chord"),("A","C","AC — diagonal"),
        ("B","C","BC — diagonal"),("A","D","AD — diagonal"),
        ("B","D","BD — diagonal"),("C","D","CD — added top chord"),
    ]
    fig = go.Figure()
    for start, end, label in members:
        added = (start, end) == ("C", "D")
        _add_member(fig, nodes, start, end, label,
                    color="#dc2626" if added else "#1e3a5f",
                    width=5.0 if added else 3.0)
    _add_nodes(fig, nodes)
    return _layout(fig, "Optimization topology — added member CD in red")


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
