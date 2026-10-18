"""Interactive lesson: how static determinacy affects 2D truss optimization.

The model is deliberately small for teaching purposes. It uses a linear-elastic
2D direct-stiffness solver and SLSQP to minimize material volume. It does not
check member buckling, connections, fatigue, fabrication, or a design code.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import minimize

E_KN_M2 = 200e6  # 200 GPa expressed in kN/m^2
AREA_BOUNDS_MM2 = (100.0, 5000.0)

# Four-joint, 4 m-span teaching truss. C and D are symmetrically placed.
NODES = {
    "A": (0.0, 0.0),
    "B": (4.0, 0.0),
    "C": (1.2, 3.0),
    "D": (2.8, 3.0),
}

# With A pinned and B on a roller: m=5, r=3, j=4 -> m+r-2j=0.
BASE_MEMBERS = [
    ("A", "B"),
    ("A", "C"),
    ("B", "C"),
    ("A", "D"),
    ("B", "D"),
]
# Adding CD gives m=6, r=3, j=4 -> m+r-2j=1 (one degree by count).
EXTRA_MEMBER = ("C", "D")


def _solve(area_mm2, members, load_each_kN=50.0):
    """Solve a pin-jointed plane truss using the direct stiffness method."""
    areas = np.asarray(area_mm2, dtype=float)
    if len(areas) != len(members):
        raise ValueError("Supply one cross-sectional area for every member.")
    if np.any(areas <= 0):
        raise ValueError("All member areas must be positive.")
    if load_each_kN <= 0:
        raise ValueError("The applied load must be positive.")

    node_names = list(NODES)
    node_index = {name: i for i, name in enumerate(node_names)}
    ndof = 2 * len(node_names)
    K = np.zeros((ndof, ndof), dtype=float)
    member_data = []

    for area, (ni, nj) in zip(areas, members):
        xi, yi = NODES[ni]
        xj, yj = NODES[nj]
        dx, dy = xj - xi, yj - yi
        length = float(np.hypot(dx, dy))
        if length <= 0:
            raise ValueError("A truss member cannot have zero length.")
        c, s = dx / length, dy / length
        area_m2 = area * 1e-6
        axial_stiffness = E_KN_M2 * area_m2 / length
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
            "length_m": length,
            "area_mm2": float(area),
            "c": c,
            "s": s,
            "dofs": dofs,
            "axial_stiffness": axial_stiffness,
        })

    F = np.zeros(ndof, dtype=float)
    # Same downward load at top joints C and D for both topologies.
    F[2 * node_index["C"] + 1] = -float(load_each_kN)
    F[2 * node_index["D"] + 1] = -float(load_each_kN)

    # A is pinned (uA=vA=0); B is a roller (vB=0).
    fixed = [2 * node_index["A"], 2 * node_index["A"] + 1,
             2 * node_index["B"] + 1]
    free = [i for i in range(ndof) if i not in fixed]
    Kff = K[np.ix_(free, free)]
    d = np.zeros(ndof, dtype=float)
    try:
        d[free] = np.linalg.solve(Kff, F[free])
    except np.linalg.LinAlgError as exc:
        raise ValueError(
            "The stiffness matrix is singular. Check truss stability and supports."
        ) from exc

    member_results = []
    for md in member_data:
        dofs = md["dofs"]
        du = d[dofs[2]] - d[dofs[0]]
        dv = d[dofs[3]] - d[dofs[1]]
        extension = md["c"] * du + md["s"] * dv
        force_kN = md["axial_stiffness"] * extension
        # kN and mm^2 -> MPa. Positive force means tension.
        stress_mpa = force_kN * 1000.0 / md["area_mm2"]
        member_results.append({
            **md,
            "force_kN": float(force_kN),
            "stress_MPa": float(stress_mpa),
            "type": ("Tension" if force_kN > 1e-7 else
                     "Compression" if force_kN < -1e-7 else "Zero"),
        })

    displacements = {
        name: (float(d[2 * i] * 1000.0), float(d[2 * i + 1] * 1000.0))
        for name, i in node_index.items()
    }
    max_displacement = max(float(np.hypot(*uv)) for uv in displacements.values())
    # For a common material, minimizing volume also minimizes mass and self-weight.
    volume_litres = sum(md["length_m"] * md["area_mm2"] for md in member_data) / 1000.0

    return {
        "members": member_results,
        "displacements_mm": displacements,
        "max_displacement_mm": max_displacement,
        "volume_litres": float(volume_litres),
        "count_members": len(members),
        "count_joints": len(NODES),
        "count_reactions": len(fixed),
        "determinacy_index": len(members) + len(fixed) - 2 * len(NODES),
    }


def solve_design(redundant=True, areas_mm2=None, load_each_kN=50.0):
    """Analyse either the five-member determinate layout or the extra-chord layout."""
    members = BASE_MEMBERS + ([EXTRA_MEMBER] if redundant else [])
    if areas_mm2 is None:
        areas_mm2 = [800.0] * len(members)
    return _solve(areas_mm2, members, load_each_kN)


def optimize_design(
    redundant=True,
    load_each_kN=50.0,
    allowable_stress_mpa=150.0,
    max_displacement_mm=4.0,
):
    """Minimize volume with area bounds, axial stress limits, and a nodal-displacement limit."""
    members = BASE_MEMBERS + ([EXTRA_MEMBER] if redundant else [])
    member_lengths = np.array([
        np.hypot(NODES[j][0] - NODES[i][0], NODES[j][1] - NODES[i][1])
        for i, j in members
    ])
    n = len(members)

    def objective(areas):
        # Litres of material; density and gravity are constant between designs.
        return float(np.dot(member_lengths, areas) / 1000.0)

    def constraints(areas):
        response = _solve(areas, members, load_each_kN)
        stresses = np.array([m["stress_MPa"] for m in response["members"]])
        stress_margins = np.r_[
            allowable_stress_mpa - stresses,
            allowable_stress_mpa + stresses,
        ]
        displacement_margin = np.array([
            max_displacement_mm - response["max_displacement_mm"]
        ])
        # SLSQP inequality constraints must be >= 0.
        return np.r_[stress_margins, displacement_margin]

    bounds = [AREA_BOUNDS_MM2] * n
    constraints_spec = [{"type": "ineq", "fun": constraints}]
    result = minimize(
        objective,
        np.full(n, 1000.0),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints_spec,
        options={"maxiter": 160, "ftol": 1e-7, "disp": False},
    )
    if not result.success:
        # A second start can help when a different constraint becomes active.
        result = minimize(
            objective,
            np.full(n, 2000.0),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints_spec,
            options={"maxiter": 240, "ftol": 1e-7, "disp": False},
        )

    design = _solve(result.x, members, load_each_kN)
    margins = constraints(result.x)
    design.update({
        "areas_mm2": [float(a) for a in result.x],
        "success": bool(result.success),
        "feasible": bool(np.min(margins) >= -1e-3),
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


def _member_table(response):
    return pd.DataFrame([
        {
            "Member": m["member"],
            "Area (mm²)": round(m["area_mm2"], 1),
            "Force (kN)": round(m["force_kN"], 2),
            "Type": m["type"],
            "Stress (MPa)": round(m["stress_MPa"], 2),
        }
        for m in response["members"]
    ])


def render_lab():
    """Render the interactive lesson embedded in the sixth tutorial."""
    st.markdown("### Interactive Optimization Lab")
    st.markdown(
        "Use the same span, supports, material, and loading for both layouts. "
        "The determinate layout has five members; adding the top chord **CD** "
        "creates one degree of static indeterminacy by the count."
    )
    st.caption(
        "The crossed diagonals AD and BC pass one another without a pin joint "
        "at their intersection in this idealized connectivity."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        load_each = st.slider(
            "Downward load at each top joint (kN)", 20, 80, 50, 10,
            key="detopt_load",
        )
    with c2:
        allowable = st.select_slider(
            "Allowable axial stress (MPa)", options=[100, 125, 150, 175, 200],
            value=150, key="detopt_stress",
        )
    with c3:
        displacement_limit = st.select_slider(
            "Maximum nodal displacement (mm)", options=[2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0],
            value=4.0, key="detopt_displacement",
        )

    st.caption(
        "Steel modulus: 200 GPa. Areas are bounded between 100 and 5,000 mm². "
        "The model assumes pin-jointed axial members and linear-elastic behavior."
    )

    st.markdown("#### Experiment 1 — Does member stiffness change force sharing?")
    extra_area = st.slider(
        "Area of added redundant member CD (mm²)", 100, 2000, 800, 100,
        key="detopt_extra_area",
    )
    det_response = solve_design(
        redundant=False,
        areas_mm2=[800.0] * len(BASE_MEMBERS),
        load_each_kN=float(load_each),
    )
    ind_response = solve_design(
        redundant=True,
        areas_mm2=[800.0] * len(BASE_MEMBERS) + [float(extra_area)],
        load_each_kN=float(load_each),
    )

    count_cols = st.columns(2)
    for col, label, response in [
        (count_cols[0], "Determinate layout", det_response),
        (count_cols[1], "Redundant layout", ind_response),
    ]:
        with col:
            index = response["determinacy_index"]
            if index == 0:
                classification = "determinate by count"
            elif index > 0:
                classification = f"indeterminate by count (degree {index})"
            else:
                classification = "unstable by count (needs further checks)"
            st.markdown(f"**{label}**")
            st.metric("Members / reactions / joints",
                      f'{response["count_members"]} / {response["count_reactions"]} / {response["count_joints"]}')
            st.metric("m + r − 2j", f"{index:+d}")
            st.caption(classification)

    det_forces = {m["member"]: m["force_kN"] for m in det_response["members"]}
    ind_forces = {m["member"]: m["force_kN"] for m in ind_response["members"]}
    member_order = ["AB", "AC", "BC", "AD", "BD", "CD"]
    force_table = pd.DataFrame([
        {
            "Member": name,
            "Determinate force (kN)": round(det_forces[name], 2) if name in det_forces else np.nan,
            "Redundant force (kN)": round(ind_forces[name], 2) if name in ind_forces else np.nan,
        }
        for name in member_order
    ])
    st.dataframe(force_table, use_container_width=True, hide_index=True)
    st.bar_chart(force_table.set_index("Member"))
    st.info(
        "In a statically determinate truss, equilibrium fixes the member-force "
        "distribution for this geometry and loading; changing areas alters stress "
        "and displacement, not the equilibrium force solution. In the redundant "
        "layout, force sharing depends on member stiffness EA/L, so changing CD's "
        "area can change forces in other members too."
    )

    st.markdown("#### Experiment 2 — Optimize each layout")
    st.write(
        "The optimizer minimizes total material volume, proportional to weight for "
        "the same material, while enforcing the selected stress and displacement limits."
    )
    with st.spinner("Optimizing both layouts…"):
        opt_det = _cached_optimize(False, float(load_each), float(allowable),
                                   float(displacement_limit))
        opt_ind = _cached_optimize(True, float(load_each), float(allowable),
                                   float(displacement_limit))

    opt_rows = []
    for result in (opt_det, opt_ind):
        max_stress = max(abs(m["stress_MPa"]) for m in result["members"])
        opt_rows.append({
            "Layout": result["topology"],
            "Solver status": "Feasible" if result["feasible"] else "Check result",
            "Material volume (L)": round(result["objective_litres"], 3),
            "Max displacement (mm)": round(result["max_displacement_mm"], 3),
            "Max |stress| (MPa)": round(max_stress, 2),
        })
    st.dataframe(pd.DataFrame(opt_rows), use_container_width=True, hide_index=True)

    if opt_det["feasible"] and opt_ind["feasible"]:
        pct = (opt_ind["objective_litres"] / opt_det["objective_litres"] - 1.0) * 100.0
        if pct < -0.05:
            comparison = f"Under these constraints, the redundant layout uses about {abs(pct):.1f}% less material in this model."
        elif pct > 0.05:
            comparison = f"Under these constraints, the redundant layout uses about {pct:.1f}% more material in this model."
        else:
            comparison = "Under these constraints, the two optimized layouts use almost the same material."
        st.markdown(f"**What the optimization found:** {comparison}")
        st.caption(
            "This result is specific to the selected geometry, loads, area bounds, "
            "and constraints. Redundancy is not automatically lighter or heavier."
        )
    else:
        st.warning(
            "At least one optimizer result did not satisfy all selected constraints. "
            "Try a higher allowable stress or a larger displacement limit."
        )

    st.markdown("##### Optimized member sizes")
    o1, o2 = st.columns(2)
    with o1:
        st.markdown("**Determinate layout**")
        st.dataframe(_member_table(opt_det), use_container_width=True, hide_index=True)
    with o2:
        st.markdown("**Redundant layout**")
        st.dataframe(_member_table(opt_ind), use_container_width=True, hide_index=True)

    st.warning(
        "Teaching model only: this experiment checks axial stress and nodal displacement. "
        "It does not check compression-member buckling, yielding rules, joints, fatigue, "
        "fabrication limits, load combinations, or IS-code compliance. Do not use its "
        "sizes directly for a real structure."
    )
