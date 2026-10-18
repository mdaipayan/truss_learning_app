"""Responsive, interactive lesson on determinacy and 2D truss optimization.

Educational assumptions:
* linear-elastic pin-jointed bars and small displacements;
* loads applied at joints;
* A is pinned and B is a vertical roller;
* sizing objective is material volume for one material;
* stress and displacement constraints are checked, but buckling, connections,
  fatigue, fabrication constraints, load combinations and design-code checks are not.

Positive member force = tension; negative member force = compression.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.optimize import minimize

AREA_BOUNDS_MM2 = (100.0, 5000.0)
DEFAULT_E_GPA = 200.0

# Four-joint, 4 m-span teaching truss.
NODES = {
    "A": (0.0, 0.0),
    "B": (4.0, 0.0),
    "C": (1.2, 3.0),
    "D": (2.8, 3.0),
}

# Stable, determinate by count: m=5, r=3, j=4, m+r-2j=0.
BASE_MEMBERS = [
    ("A", "B"),
    ("A", "C"),
    ("B", "C"),
    ("A", "D"),
    ("B", "D"),
]
# Added top chord gives one degree of static indeterminacy by count.
EXTRA_MEMBER = ("C", "D")
MEMBER_ORDER = ["AB", "AC", "BC", "AD", "BD", "CD"]


def _solve(
    areas_mm2,
    members,
    load_each_kN=50.0,
    member_moduli_gpa=None,
):
    """Solve a plane truss by the global direct-stiffness method.

    E is supplied per member so the what-if lab can change CD's modulus.
    For E in GPa, A in mm², and L in m, EA/L = E_GPa*A_mm2/L in kN/m.
    """
    areas = np.asarray(areas_mm2, dtype=float)
    count = len(members)
    if areas.ndim != 1 or len(areas) != count:
        raise ValueError("Supply one cross-sectional area for every member.")
    if np.any(~np.isfinite(areas)) or np.any(areas <= 0):
        raise ValueError("All member areas must be finite and positive.")
    if not np.isfinite(load_each_kN) or load_each_kN <= 0:
        raise ValueError("The applied load must be finite and positive.")

    if member_moduli_gpa is None:
        moduli = np.full(count, DEFAULT_E_GPA, dtype=float)
    else:
        moduli = np.asarray(member_moduli_gpa, dtype=float)
    if moduli.ndim != 1 or len(moduli) != count:
        raise ValueError("Supply one Young's modulus value for every member.")
    if np.any(~np.isfinite(moduli)) or np.any(moduli <= 0):
        raise ValueError("Young's modulus values must be finite and positive.")

    node_names = list(NODES)
    node_index = {name: i for i, name in enumerate(node_names)}
    ndof = 2 * len(node_names)
    K = np.zeros((ndof, ndof), dtype=float)
    member_data = []

    for idx, ((ni, nj), area, E_gpa) in enumerate(zip(members, areas, moduli)):
        xi, yi = NODES[ni]
        xj, yj = NODES[nj]
        dx, dy = xj - xi, yj - yi
        length = float(np.hypot(dx, dy))
        if length <= 0:
            raise ValueError(f"Member {ni}{nj} has zero length.")
        c, s = dx / length, dy / length
        axial_stiffness = float(E_gpa * area / length)  # kN/m
        ke = axial_stiffness * np.array([
            [c*c, c*s, -c*c, -c*s],
            [c*s, s*s, -c*s, -s*s],
            [-c*c, -c*s, c*c, c*s],
            [-c*s, -s*s, c*s, s*s],
        ])
        dofs = [
            2 * node_index[ni], 2 * node_index[ni] + 1,
            2 * node_index[nj], 2 * node_index[nj] + 1,
        ]
        K[np.ix_(dofs, dofs)] += ke
        member_data.append({
            "member": f"{ni}{nj}",
            "start": ni,
            "end": nj,
            "length_m": length,
            "area_mm2": float(area),
            "modulus_gpa": float(E_gpa),
            "c": float(c),
            "s": float(s),
            "dofs": dofs,
            "axial_stiffness": axial_stiffness,
        })

    F = np.zeros(ndof, dtype=float)
    F[2 * node_index["C"] + 1] = -float(load_each_kN)
    F[2 * node_index["D"] + 1] = -float(load_each_kN)

    # A pin restrains ux and uy; B roller restrains uy only.
    fixed = [
        2 * node_index["A"],
        2 * node_index["A"] + 1,
        2 * node_index["B"] + 1,
    ]
    free = [i for i in range(ndof) if i not in fixed]
    Kff = K[np.ix_(free, free)]
    d = np.zeros(ndof, dtype=float)
    try:
        d[free] = np.linalg.solve(Kff, F[free])
    except np.linalg.LinAlgError as exc:
        raise ValueError(
            "The reduced stiffness matrix is singular. Check geometry and supports."
        ) from exc

    member_results = []
    for md in member_data:
        dofs = md["dofs"]
        relative_u = d[dofs[2]] - d[dofs[0]]
        relative_v = d[dofs[3]] - d[dofs[1]]
        extension = md["c"] * relative_u + md["s"] * relative_v
        force_kN = md["axial_stiffness"] * extension
        # kN * 1000 / mm² gives N/mm² = MPa.
        stress_mpa = force_kN * 1000.0 / md["area_mm2"]
        tol = 1e-7
        force_type = (
            "Tension" if force_kN > tol else
            "Compression" if force_kN < -tol else "Zero-force"
        )
        member_results.append({
            **md,
            "force_kN": float(force_kN),
            "stress_MPa": float(stress_mpa),
            "type": force_type,
        })

    displacements_mm = {
        name: (
            float(d[2 * i] * 1000.0),
            float(d[2 * i + 1] * 1000.0),
        )
        for name, i in node_index.items()
    }
    max_displacement = max(
        float(np.hypot(ux, uy)) for ux, uy in displacements_mm.values()
    )
    # For one common material, volume is proportional to mass and self-weight.
    volume_litres = sum(
        md["length_m"] * md["area_mm2"] for md in member_data
    ) / 1000.0
    reactions = K @ d - F

    return {
        "nodes": NODES.copy(),
        "members": member_results,
        "displacements_mm": displacements_mm,
        "max_displacement_mm": max_displacement,
        "volume_litres": float(volume_litres),
        "reactions_kN": {
            "Ax": float(reactions[2 * node_index["A"]]),
            "Ay": float(reactions[2 * node_index["A"] + 1]),
            "By": float(reactions[2 * node_index["B"] + 1]),
        },
        "count_members": len(members),
        "count_joints": len(NODES),
        "count_reactions": len(fixed),
        "determinacy_index": len(members) + len(fixed) - 2 * len(NODES),
        "load_each_kN": float(load_each_kN),
    }


def solve_design(redundant=True, areas_mm2=None, load_each_kN=50.0,
                 member_moduli_gpa=None):
    """Analyse either the five-member determinate layout or the added-CD layout."""
    members = BASE_MEMBERS + ([EXTRA_MEMBER] if redundant else [])
    count = len(members)
    if areas_mm2 is None:
        areas_mm2 = [800.0] * count
    if member_moduli_gpa is None:
        member_moduli_gpa = [DEFAULT_E_GPA] * count
    return _solve(
        areas_mm2, members, load_each_kN,
        member_moduli_gpa=member_moduli_gpa,
    )


def optimize_design(
    redundant=True,
    load_each_kN=50.0,
    allowable_stress_mpa=150.0,
    max_displacement_mm=4.0,
):
    """Minimize volume subject to axial-stress and nodal-displacement limits."""
    members = BASE_MEMBERS + ([EXTRA_MEMBER] if redundant else [])
    lengths = np.array([
        np.hypot(NODES[j][0] - NODES[i][0], NODES[j][1] - NODES[i][1])
        for i, j in members
    ])
    n = len(members)

    def objective(areas):
        return float(np.dot(lengths, areas) / 1000.0)

    def margins(areas):
        response = _solve(areas, members, load_each_kN)
        stresses = np.array([m["stress_MPa"] for m in response["members"]])
        stress_margins = np.r_[
            allowable_stress_mpa - stresses,
            allowable_stress_mpa + stresses,
        ]
        displacement_margin = np.array([
            max_displacement_mm - response["max_displacement_mm"]
        ])
        return np.r_[stress_margins, displacement_margin]

    constraint_spec = [{"type": "ineq", "fun": margins}]
    bounds = [AREA_BOUNDS_MM2] * n
    result = minimize(
        objective,
        np.full(n, 1000.0),
        method="SLSQP",
        bounds=bounds,
        constraints=constraint_spec,
        options={"maxiter": 200, "ftol": 1e-8, "disp": False},
    )
    if not result.success or np.min(margins(result.x)) < -1e-3:
        retry = minimize(
            objective,
            np.full(n, 2500.0),
            method="SLSQP",
            bounds=bounds,
            constraints=constraint_spec,
            options={"maxiter": 300, "ftol": 1e-8, "disp": False},
        )
        current_feasible = bool(np.min(margins(result.x)) >= -1e-3)
        retry_feasible = bool(np.min(margins(retry.x)) >= -1e-3)
        if retry_feasible and (
            not current_feasible or (retry.success and retry.fun < result.fun)
        ):
            result = retry

    design = _solve(result.x, members, load_each_kN)
    final_margins = margins(result.x)
    design.update({
        "areas_mm2": [float(a) for a in result.x],
        "success": bool(result.success),
        "feasible": bool(np.min(final_margins) >= -1e-3),
        "optimization_message": str(result.message),
        "objective_litres": float(result.fun),
        "allowable_stress_MPa": float(allowable_stress_mpa),
        "max_displacement_limit_mm": float(max_displacement_mm),
        "topology": "Indeterminate" if redundant else "Determinate",
    })
    return design


@st.cache_data(show_spinner=False)
def _cached_optimize(redundant, load_each_kN, allowable_stress_mpa, max_displacement_mm):
    return optimize_design(
        redundant=redundant,
        load_each_kN=load_each_kN,
        allowable_stress_mpa=allowable_stress_mpa,
        max_displacement_mm=max_displacement_mm,
    )


def member_report(response, allowable_stress_mpa):
    """Return the teaching report with a utilization ratio for every member."""
    rows = []
    for member in response["members"]:
        stress = member["stress_MPa"]
        utilization = abs(stress) / allowable_stress_mpa
        rows.append({
            "Member ID": member["member"],
            "Length L (m)": member["length_m"],
            "Area A (mm²)": member["area_mm2"],
            "Internal force P (kN)": member["force_kN"],
            "Axial stress σ (MPa)": stress,
            "Utilization |σ|/σallow": utilization,
            "Force type": member["type"],
        })
    return pd.DataFrame(rows)


def _styled_report(report):
    """Soft-red row highlighting when utilization exceeds 1.0."""
    def style_row(row):
        if float(row["Utilization |σ|/σallow"]) > 1.0 + 1e-8:
            return ["background-color: #fee2e2; color: #991b1b;"] * len(row)
        return [""] * len(row)
    return report.style.apply(style_row, axis=1).format({
        "Length L (m)": "{:.3f}",
        "Area A (mm²)": "{:.1f}",
        "Internal force P (kN)": "{:+.2f}",
        "Axial stress σ (MPa)": "{:+.2f}",
        "Utilization |σ|/σallow": "{:.3f}",
    })


def plot_truss_plotly(response, redundant, show_deflected=False,
                      exaggeration=50, allowable_stress_mpa=150.0,
                      title=None):
    """Create a responsive interactive member-force and deformation plot."""
    fig = go.Figure()
    nodes = response["nodes"]
    disp = response["displacements_mm"]
    max_abs_force = max(
        [abs(m["force_kN"]) for m in response["members"]] + [1.0]
    )
    member_results = response["members"]

    # Faint original mesh sits behind the colored deformed mesh.
    if show_deflected:
        for md in member_results:
            xi, yi = nodes[md["start"]]
            xj, yj = nodes[md["end"]]
            fig.add_trace(go.Scatter(
                x=[xi, xj], y=[yi, yj],
                mode="lines",
                line={"color": "#cbd5e1", "width": 1.4, "dash": "dash"},
                hoverinfo="skip",
                showlegend=False,
            ))
        fig.add_trace(go.Scatter(
            x=[p[0] for p in nodes.values()],
            y=[p[1] for p in nodes.values()],
            mode="markers+text",
            text=list(nodes.keys()),
            textposition="bottom center",
            marker={"size": 7, "color": "#94a3b8"},
            textfont={"size": 11, "color": "#64748b"},
            name="Undeformed joints",
            hoverinfo="skip",
        ))

    for md in member_results:
        xi, yi = nodes[md["start"]]
        xj, yj = nodes[md["end"]]
        ux_i, uy_i = disp[md["start"]]
        ux_j, uy_j = disp[md["end"]]
        if show_deflected:
            xi += ux_i / 1000.0 * exaggeration
            yi += uy_i / 1000.0 * exaggeration
            xj += ux_j / 1000.0 * exaggeration
            yj += uy_j / 1000.0 * exaggeration

        force = md["force_kN"]
        util = abs(md["stress_MPa"]) / allowable_stress_mpa
        if md["type"] == "Compression":
            color = "#dc2626"
        elif md["type"] == "Tension":
            color = "#2563eb"
        else:
            color = "#cbd5e1"
        # Thickness communicates absolute force, capped to avoid dominating a panel.
        width = 1.8 + 4.2 * min(abs(force) / max_abs_force, 1.0)
        if util > 1.0:
            width += 1.0

        fig.add_trace(go.Scatter(
            x=[xi, xj], y=[yi, yj],
            mode="lines",
            line={"color": color, "width": width},
            name=f"{md['member']} — {md['type']}",
            showlegend=False,
            customdata=[[
                md["member"], md["length_m"], md["area_mm2"], force,
                md["stress_MPa"], util, md["type"], md["modulus_gpa"],
            ]] * 2,
            hovertemplate=(
                "<b>Member %{customdata[0]}</b><br>"
                "Length: %{customdata[1]:.3f} m<br>"
                "Area: %{customdata[2]:.1f} mm²<br>"
                "Axial force: %{customdata[3]:+.2f} kN<br>"
                "Stress: %{customdata[4]:+.2f} MPa<br>"
                "Utilization: %{customdata[5]:.3f}<br>"
                "Type: %{customdata[6]}<br>"
                "E: %{customdata[7]:.1f} GPa<extra></extra>"
            ),
        ))

    # Draw node labels on the selected (possibly deflected) coordinates.
    label_x, label_y, label_text = [], [], []
    for name, (x, y) in nodes.items():
        ux, uy = disp[name]
        if show_deflected:
            x += ux / 1000.0 * exaggeration
            y += uy / 1000.0 * exaggeration
        label_x.append(x)
        label_y.append(y)
        label_text.append(name)
    fig.add_trace(go.Scatter(
        x=label_x, y=label_y,
        mode="markers+text",
        text=label_text,
        textposition="top center",
        marker={"size": 7, "color": "#0f172a"},
        textfont={"size": 11, "color": "#0f172a"},
        name="Joints",
        hovertemplate="Joint %{text}<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        title=title or ("Redundant truss" if redundant else "Determinate truss"),
        margin={"l": 20, "r": 20, "t": 42, "b": 20},
        height=340,
        autosize=True,
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Arial, sans-serif", "size": 12, "color": "#0f172a"},
        hovermode="closest",
    )
    fig.update_xaxes(
        title="x (m)", showgrid=True, gridcolor="#f1f5f9",
        zeroline=False, automargin=True,
    )
    fig.update_yaxes(
        title="y (m)", showgrid=True, gridcolor="#f1f5f9",
        zeroline=False, scaleanchor="x", scaleratio=1, automargin=True,
    )
    return fig


def _render_optimization_controls():
    """Keep model knobs grouped so they don't dominate a narrow screen."""
    with st.expander("Model and optimization controls", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            load_each = st.slider(
                "Load at each top joint (kN)", 20, 80, 50, 10, key="detopt_load"
            )
        with c2:
            allowable = st.select_slider(
                "Allowable axial stress (MPa)",
                options=[100, 125, 150, 175, 200], value=150,
                key="detopt_stress",
            )
        with c3:
            displacement_limit = st.select_slider(
                "Maximum nodal displacement (mm)",
                options=[2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0], value=4.0,
                key="detopt_displacement",
            )
    return float(load_each), float(allowable), float(displacement_limit)


def render_lab():
    """Render the interactive lesson embedded in the sixth tutorial."""
    st.markdown("### Interactive Optimization Lab")
    st.markdown(
        "Compare two layouts under the same span, supports, material and loading. "
        "The determinate layout has five members; adding top chord **CD** gives "
        "one degree of static indeterminacy by the count."
    )
    st.caption(
        "Members AD and BC cross geometrically without being connected at their "
        "intersection; only the labeled joints are structural nodes."
    )

    load_each, allowable, displacement_limit = _render_optimization_controls()

    with st.expander("Experiment 1 — What if CD becomes stiffer?", expanded=True):
        mode = st.radio(
            "Change which property of member CD?",
            ["Cross-sectional area A", "Young's modulus E"],
            horizontal=True,
            key="detopt_sensitivity_mode",
        )
        control_a, control_b = st.columns(2)
        with control_a:
            if mode == "Cross-sectional area A":
                cd_area = st.slider(
                    "Area of CD (mm²)", 100, 2000, 800, 100,
                    key="detopt_extra_area",
                )
                cd_E = 200.0
            else:
                cd_E = st.slider(
                    "Young's modulus of CD (GPa)", 50, 400, 200, 25,
                    key="detopt_extra_E",
                )
                cd_area = 800
        with control_b:
            cd_length = float(np.hypot(
                NODES["D"][0] - NODES["C"][0],
                NODES["D"][1] - NODES["C"][1],
            ))
            cd_stiffness = cd_E * cd_area / cd_length
            st.metric("Axial stiffness EA/L of CD", f"{cd_stiffness:,.1f} kN/m")
            st.caption("For this unit convention: E in GPa, A in mm² and L in m.")

        det = solve_design(
            redundant=False,
            areas_mm2=[800.0] * len(BASE_MEMBERS),
            load_each_kN=load_each,
        )
        redundant_areas = [800.0] * len(BASE_MEMBERS) + [float(cd_area)]
        redundant_E = [DEFAULT_E_GPA] * len(BASE_MEMBERS) + [float(cd_E)]
        ind = solve_design(
            redundant=True,
            areas_mm2=redundant_areas,
            load_each_kN=load_each,
            member_moduli_gpa=redundant_E,
        )

        count_cols = st.columns(2)
        for col, label, response in [
            (count_cols[0], "Determinate", det),
            (count_cols[1], "Indeterminate by count", ind),
        ]:
            with col:
                index = response["determinacy_index"]
                col.markdown(f"**{label}**")
                col.metric("Members / reactions / joints",
                           f'{response["count_members"]} / {response["count_reactions"]} / {response["count_joints"]}')
                col.metric("i = m + r − 2j", f"{index:+d}")
        st.info(
            "In the determinate layout, member forces are set by equilibrium for "
            "the same geometry and loads. In the redundant layout, the CD stiffness "
            "changes compatibility and can redistribute forces among members. "
            "Changing A or E matters through the relative axial stiffness EA/L."
        )

        det_force = {m["member"]: m["force_kN"] for m in det["members"]}
        ind_force = {m["member"]: m["force_kN"] for m in ind["members"]}
        det_type = {m["member"]: m["type"] for m in det["members"]}
        ind_type = {m["member"]: m["type"] for m in ind["members"]}
        comparison = pd.DataFrame([
            {
                "Member": member_id,
                "Determinate P (kN)": det_force.get(member_id, np.nan),
                "Determinate type": det_type.get(member_id, "—"),
                "Redundant P (kN)": ind_force.get(member_id, np.nan),
                "Redundant type": ind_type.get(member_id, "—"),
            }
            for member_id in MEMBER_ORDER
        ])
        st.dataframe(
            comparison.style.format({
                "Determinate P (kN)": "{:+.2f}",
                "Redundant P (kN)": "{:+.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

        force_view = st.radio(
            "Inspect the current force map",
            ["Determinate", "Redundant (current CD setting)"],
            horizontal=True,
            key="detopt_sensitivity_force_view",
        )
        view_is_redundant = force_view.startswith("Redundant")
        view_response = ind if view_is_redundant else det
        view_fig = plot_truss_plotly(
            view_response,
            redundant=view_is_redundant,
            show_deflected=False,
            allowable_stress_mpa=allowable,
            title=f"{force_view} — current what-if setting",
        )
        st.plotly_chart(
            view_fig,
            use_container_width=True,
            config={"responsive": True, "displaylogo": False},
            key="detopt_sensitivity_force_plot",
        )

        with st.expander("Why the slider changes force sharing", expanded=False):
            st.markdown(r"""
**Axial member stiffness**

\[
k_i=\frac{E_i A_i}{L_i}
\]

For a determinate truss, equilibrium fixes the ideal member-force solution.
Area changes alter stress and deformation but not those equilibrium forces.

For an indeterminate truss, equilibrium alone is insufficient. The solution
also satisfies displacement compatibility, so changing a redundant member's
\(E_iA_i/L_i\) can redistribute forces. If \(A\) is multiplied by a factor
and \(E\) is divided by the same factor, the member's axial stiffness is
unchanged (for fixed length), so this linear-elastic model predicts the same
stiffness contribution.
""")

    st.markdown("### Experiment 2 — Minimize the material volume")
    st.markdown(
        r"Minimize \(V=\sum_i L_iA_i\), subject to stress and displacement limits."
    )
    with st.spinner("Optimizing both layouts…"):
        opt_det = _cached_optimize(False, load_each, allowable, displacement_limit)
        opt_ind = _cached_optimize(True, load_each, allowable, displacement_limit)

    result_rows = []
    for result in (opt_det, opt_ind):
        max_stress = max(abs(m["stress_MPa"]) for m in result["members"])
        result_rows.append({
            "Layout": result["topology"],
            "Status": "Feasible" if result["feasible"] else "Review constraints",
            "Material volume (L)": result["objective_litres"],
            "Max nodal displacement (mm)": result["max_displacement_mm"],
            "Max |stress| (MPa)": max_stress,
        })
    summary = pd.DataFrame(result_rows)
    st.dataframe(
        summary.style.format({
            "Material volume (L)": "{:.3f}",
            "Max nodal displacement (mm)": "{:.3f}",
            "Max |stress| (MPa)": "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    if opt_det["feasible"] and opt_ind["feasible"]:
        difference_pct = (
            opt_ind["objective_litres"] / opt_det["objective_litres"] - 1.0
        ) * 100.0
        if difference_pct < -0.05:
            insight = f"The redundant solution uses about {abs(difference_pct):.1f}% less material in this selected model."
        elif difference_pct > 0.05:
            insight = f"The redundant solution uses about {difference_pct:.1f}% more material in this selected model."
        else:
            insight = "The two optimized layouts use almost the same material in this selected model."
        st.markdown(f"**Optimization insight:** {insight}")
        st.caption(
            "This conclusion is conditional on the chosen geometry, loads, sizing bounds, "
            "and constraints. Static indeterminacy alone does not guarantee a lighter design."
        )
    else:
        st.warning(
            "At least one optimization result is not feasible under the current settings. "
            "Increase the displacement limit or allowable stress, then try again."
        )

    # Visual controls are kept together; two charts wrap to one column on mobile.
    with st.expander("Interactive force and deformation views", expanded=True):
        show_deflected = st.toggle(
            "Show Deflected Shape",
            value=False,
            key="detopt_show_deflected",
        )
        if show_deflected:
            scale = st.slider(
                "Deformation exaggeration scale", 10, 100, 50, 10,
                key="detopt_deformation_scale",
            )
            st.caption(
                "The original mesh appears as dashed gray lines; the colored solid "
                "mesh shows the calculated displacement multiplied by this scale."
            )
        else:
            scale = 1

        left, right = st.columns(2)
        for col, result, is_redundant, label in [
            (left, opt_det, False, "Optimized determinate layout"),
            (right, opt_ind, True, "Optimized redundant layout"),
        ]:
            with col:
                st.markdown(f"**{label}**")
                fig = plot_truss_plotly(
                    result,
                    redundant=is_redundant,
                    show_deflected=show_deflected,
                    exaggeration=scale,
                    allowable_stress_mpa=allowable,
                    title=label,
                )
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"responsive": True, "displaylogo": False},
                    key=f"detopt_plot_{'ind' if is_redundant else 'det'}",
                )

        st.markdown(
            "**Legend:** 🔴 compression · 🔵 tension · light gray zero-force members. "
            "Member thickness scales with absolute axial force; overstress increases "
            "line weight and is identified in the table."
        )

    st.markdown("### Member force and utilization tables")
    report_cols = st.columns(2)
    for col, result, label in [
        (report_cols[0], opt_det, "Determinate layout"),
        (report_cols[1], opt_ind, "Redundant layout"),
    ]:
        with col:
            st.markdown(f"**{label}**")
            report = member_report(result, allowable)
            st.dataframe(
                _styled_report(report),
                use_container_width=True,
                hide_index=True,
            )
            overstressed = report[
                report["Utilization |σ|/σallow"] > 1.0 + 1e-8
            ]
            if not overstressed.empty:
                names = ", ".join(overstressed["Member ID"].astype(str))
                st.error(f"Overstress detected in: {names}")
            else:
                st.success("All reported members meet the selected axial-stress limit.")

    with st.expander("Formula cards and assumptions", expanded=False):
        st.markdown(r"""
**Degree of static indeterminacy (counting check)**

\[
i=m+r-2j
\]

Here \(m\) is the number of members, \(r\) the independent support reaction
components, and \(j\) the number of joints. The count must be paired with a
geometric stability check; it is not a stand-alone stability proof.

**Sizing optimization**

\[
\min_{\{A_i\}} V=\sum_i L_iA_i
\]

\[
|\sigma_i| \le \sigma_{\mathrm{allow}}, \qquad
\delta_j \le \delta_{\mathrm{allow}}
\]

\[
\sigma_i=\frac{P_i}{A_i},\qquad
u_i=\frac{|\sigma_i|}{\sigma_{\mathrm{allow}}}
\]

This implementation imposes the displacement limit on the magnitude of each
joint's in-plane displacement. In addition to the assumptions above, the
optimizer uses area bounds of 100–5,000 mm² and a single linear-elastic
material. It is a learning experiment, not a code-compliant design tool.
""")

    st.caption(
        "Not checked: compression-member buckling, connection strength, fatigue, "
        "fabrication limits, load combinations, self-weight feedback, or IS-code compliance. "
        "Do not use these sizes directly for construction."
    )
