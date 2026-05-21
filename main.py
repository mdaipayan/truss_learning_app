"""Truss Learning App — gamified, light-theme Streamlit UI."""

import random, re
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd

import game, diagrams, dsm_solver, solver as slv
from questions import TUTORIALS, QUESTIONS

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Truss Learning",
    page_icon="🔺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (light / elegant) ──────────────────────────────────────────────

st.markdown("""
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #f8fafc !important;
    font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
}
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    padding-top: 0.5rem;
}
.main .block-container { padding: 2rem 2.5rem 3rem; max-width: 1140px; }

/* ── Sidebar nav ── */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] button {
    background: transparent !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    font-size: 0.93em;
    padding: 0.4rem 0.8rem !important;
    transition: all 0.15s;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] button:hover {
    background: #eff6ff !important;
    border-color: #93c5fd !important;
    color: #1d4ed8 !important;
}

/* ── Card ── */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(15,23,42,.06);
}
.card-accent {
    border-left: 4px solid #2563eb;
}

/* ── Level badge ── */
.lvl-badge {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    font-weight: 700;
    font-size: 0.88em;
    padding: 4px 16px;
    border-radius: 20px;
    margin-bottom: 6px;
}

/* ── Step panel ── */
.step-complete {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.step-active {
    background: #eff6ff;
    border: 1px solid #93c5fd;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.step-locked {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    opacity: 0.6;
}

/* ── Achievement card ── */
.ach-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(15,23,42,.05);
}
.ach-card.unlocked { border-color: #2563eb; }
.ach-card.locked   { opacity: 0.45; }

/* ── Streak pill ── */
.streak-pill {
    display: inline-block;
    background: linear-gradient(90deg, #f97316, #ef4444);
    color: white;
    font-weight: 800;
    padding: 3px 12px;
    border-radius: 20px;
}

/* ── Equation box ── */
.eq-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: "Courier New", monospace;
    font-size: 0.92em;
    color: #0f172a;
    white-space: pre-wrap;
    margin: 8px 0;
}

/* ── Matrix table ── */
[data-testid="stDataFrame"] table {
    font-size: 0.82em;
    font-family: "Courier New", monospace;
}
</style>
""", unsafe_allow_html=True)

# ── Session-state init ────────────────────────────────────────────────────────

def _init():
    if "gs" not in st.session_state:
        st.session_state.gs = game.load()
    defaults = {
        "page":          "home",
        "tut_idx":       0,
        # quiz
        "quiz_pool":     None,
        "quiz_idx":      0,
        "quiz_score":    0,
        "quiz_wrong":    [],
        "quiz_answered": False,
        "quiz_selected": None,
        "quiz_topic":    None,
        "streak":        0,
        "toasts":        [],
        # interactive solver
        "sv_step":       0,
        "sv_sub":        0,
        "sv_done":       {},      # {(step,sub): float}  completed answers
        "sv_attempts":   {},      # {(step,sub): int}
        "sv_show_hint":  {},      # {(step,sub): bool}
        "sv_reactions":  {},
        "sv_forces":     {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


def go(page, **kw):
    st.session_state.page = page
    for k, v in kw.items():
        st.session_state[k] = v
    st.rerun()


def gs():
    return st.session_state.gs


def _save():
    game.save(st.session_state.gs)


def _strip(text):
    return re.sub(r"\[/?[^\]]+\]", "", text)


# ── Diagrams per tutorial ─────────────────────────────────────────────────────

DIAG_FNS = [
    diagrams.diagram_basic_truss,
    diagrams.diagram_truss_types,
    diagrams.diagram_method_joints,
    diagrams.diagram_method_sections,
    diagrams.diagram_determinacy,
]

# ── Sidebar ───────────────────────────────────────────────────────────────────

def _sidebar():
    g   = gs()
    lv  = game.get_level(g["xp"])
    xpd, xpb = game.xp_to_next_level(g["xp"])

    with st.sidebar:
        st.markdown("## 🔺 Truss Learning")
        st.divider()

        st.markdown(f'<div class="lvl-badge">{lv["icon"]} {lv["name"]}</div>',
                    unsafe_allow_html=True)
        st.caption(f"{g['xp']} XP" + (
            f"  ·  {xpd}/{xpb} to next" if xpb else "  ·  MAX LEVEL"))
        if xpb:
            st.progress(xpd / xpb)
        st.caption(f"🏅 {len(g['unlocked'])}/{len(game.ACHIEVEMENTS)} achievements")
        st.divider()

        for icon, label, pg in [
            ("🏠", "Home",              "home"),
            ("📖", "Learn",             "tutorials"),
            ("🔧", "Solve",             "solve"),
            ("🧮", "Stiffness Method",  "dsm"),
            ("⚔️", "Challenge",         "quiz_menu"),
            ("🏅", "Achievements",      "achievements"),
            ("📋", "Reference",         "reference"),
        ]:
            if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{pg}"):
                go(pg)

        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("✅", g["total_correct"])
        c2.metric("📝", g["total_answered"])
        acc = (g["total_correct"] / g["total_answered"] * 100) if g["total_answered"] else 0
        st.caption(f"Accuracy {acc:.0f}%  ·  Best streak {g['best_streak']} 🔥")


_sidebar()

for t in st.session_state.toasts:
    st.toast(f"{t['icon']} **{t['name']}** unlocked! +{t['xp']} XP", icon="🎉")
st.session_state.toasts = []

# ════════════════════════════════════════════════════════════════════════════════
# PAGES
# ════════════════════════════════════════════════════════════════════════════════

# ── Home ──────────────────────────────────────────────────────────────────────

def page_home():
    g   = gs()
    lv  = game.get_level(g["xp"])

    st.title("🔺 Truss Learning App")
    st.subheader("Master structural analysis — one concept at a time.")
    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Level",       f'{lv["icon"]} {lv["name"]}')
    c2.metric("Total XP",    g["xp"])
    c3.metric("Tutorials",   f'{len(g["tutorials_read"])}/5')
    c4.metric("Accuracy",    f'{(g["total_correct"]/g["total_answered"]*100):.0f}%'
              if g["total_answered"] else "—")

    st.write("")

    panels = [
        ("📖", "Learn",          "tutorials",
         "5 illustrated tutorials with engineering-quality diagrams. **+15 XP** each."),
        ("🔧", "Solve",          "solve",
         "Step-by-step interactive solver — fill in each unknown and check your answer."),
        ("🧮", "Stiffness Method","dsm",
         "Build the global **K** matrix, apply BCs, and solve for displacements."),
        ("⚔️", "Challenge",      "quiz_menu",
         "13 quiz questions, streaks & XP bonuses. **+20 XP** per correct answer."),
    ]

    cols = st.columns(4)
    for col, (icon, lbl, pg, desc) in zip(cols, panels):
        with col:
            st.markdown(f"#### {icon} {lbl}")
            st.caption(desc)
            if st.button(f"Open →", key=f"h_{pg}", use_container_width=True):
                go(pg)

    st.divider()
    st.markdown("#### Level Roadmap")
    cols2 = st.columns(len(game.LEVELS))
    for col, lv_info in zip(cols2, game.LEVELS):
        done = g["xp"] >= lv_info["min_xp"]
        col.markdown(f"**{lv_info['icon']} {lv_info['name']}**")
        col.caption(f"{'✅' if done else '🔒'} {lv_info['min_xp']} XP")


# ── Tutorials ─────────────────────────────────────────────────────────────────

def page_tutorials():
    g = gs()
    st.title("📖 Illustrated Tutorials")

    topics  = [t["title"] for t in TUTORIALS]
    sel     = st.radio("Select topic:", topics,
                       index=st.session_state.tut_idx, horizontal=True)
    idx     = topics.index(sel)
    st.session_state.tut_idx = idx

    st.divider()

    tut      = TUTORIALS[idx]
    was_read = idx in g["tutorials_read"]

    ch, cb = st.columns([5, 1])
    with ch:
        st.subheader(f"{idx+1}. {tut['title']}")
        st.caption(f"Topic {idx+1} of {len(TUTORIALS)}")
    with cb:
        if was_read:
            st.success("✅ Done")
        else:
            st.info("⭐ +15 XP")

    fig = DIAG_FNS[idx]()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown(_strip(tut["content"]))
    st.write("")

    cp, cm, cn = st.columns([1, 2, 1])
    with cp:
        if idx > 0 and st.button("← Previous", use_container_width=True):
            st.session_state.tut_idx = idx - 1;  st.rerun()
    with cm:
        if not was_read:
            if st.button("📖 Mark as read (+15 XP)", type="primary",
                         use_container_width=True):
                g["tutorials_read"].append(idx)
                old  = game.get_level_index(g["xp"])
                g["xp"] += 15
                new_a = game.check_achievements(g, st.session_state.streak, None, None)
                st.session_state.toasts.extend(new_a)
                if game.get_level_index(g["xp"]) > old:
                    st.balloons()
                _save();  st.rerun()
        else:
            st.button("✅ Already completed", disabled=True,
                      use_container_width=True)
    with cn:
        if idx < len(TUTORIALS)-1 and st.button("Next →", use_container_width=True):
            st.session_state.tut_idx = idx + 1;  st.rerun()


# ── Interactive Solver ────────────────────────────────────────────────────────

def page_solve():
    st.title("🔧 Interactive Truss Solver")
    st.markdown(
        "Work through the **Method of Joints** step-by-step. "
        "Enter each unknown, check your answer, and the diagram updates as you go."
    )

    # Rebuild current known state from session
    reactions = st.session_state.sv_reactions
    forces    = st.session_state.sv_forces

    left, right = st.columns([1, 1], gap="large")

    # ── Left: live diagram ────────────────────────────────────────────────────
    with left:
        cur_step = st.session_state.sv_step
        h_joint  = slv.STEPS[cur_step]["highlight"] if cur_step < len(slv.STEPS) else None
        fig = diagrams.diagram_solver_state(
            highlight_joint=h_joint,
            known_forces=forces,
            known_reactions=reactions,
        )
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # Summary table once finished
        if cur_step >= len(slv.STEPS):
            st.success("### ✅ Truss fully solved!")
            data = {
                "Member":     ["AC", "CB", "AD", "BD", "CD"],
                "Force (kN)": [forces.get(m, "—") for m in ["AC", "CB", "AD", "BD", "CD"]],
                "Type":       [
                    ("Tension" if isinstance(forces.get(m), float) and forces[m] > 0.01
                     else "Compression" if isinstance(forces.get(m), float) and forces[m] < -0.01
                     else "Zero" if isinstance(forces.get(m), float)
                     else "—")
                    for m in ["AC", "CB", "AD", "BD", "CD"]
                ],
            }
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            if st.button("🔄 Reset", type="secondary"):
                for k in ["sv_step","sv_sub","sv_done","sv_attempts",
                          "sv_show_hint","sv_reactions","sv_forces"]:
                    st.session_state[k] = {} if isinstance(
                        st.session_state[k], dict) else 0
                st.rerun()

    # ── Right: steps ──────────────────────────────────────────────────────────
    with right:
        for si, step in enumerate(slv.STEPS):
            is_active   = si == cur_step
            is_done     = si < cur_step
            is_locked   = si > cur_step

            if is_done:
                cls = "step-complete"
                ico = "✅"
            elif is_active:
                cls = "step-active"
                ico = step["icon"]
            else:
                cls = "step-locked"
                ico = "🔒"

            with st.expander(f"{ico} {step['title']}", expanded=is_active):
                if is_locked:
                    st.caption("Complete the previous step first.")
                    continue

                if is_active:
                    st.info(step["intro"])

                for sbi, sub in enumerate(step["sub"]):
                    key = (si, sbi)
                    done_val = st.session_state.sv_done.get(key)

                    if done_val is not None:
                        # Completed sub-step
                        st.success(
                            f"**{sub['label']}**  →  "
                            f"**{done_val:+.2f} {sub['unit']}**\n\n"
                            f"_{sub['expl']}_"
                        )
                        continue

                    if is_done:
                        # Step completed but sub not in sv_done (shouldn't happen)
                        continue

                    # Active sub-step
                    st.markdown(f"**{sub['label']}**")
                    st.markdown(
                        f'<div class="eq-box">{sub["eq"]}</div>',
                        unsafe_allow_html=True,
                    )

                    # Show hint?
                    show_h = st.session_state.sv_show_hint.get(key, False)
                    if show_h:
                        st.warning(f"💡 Hint: {sub['hint']}")

                    col_inp, col_btn = st.columns([2, 1])
                    with col_inp:
                        val = st.number_input(
                            f"Answer ({sub['unit']})",
                            value=0.0, step=0.1,
                            format="%.2f",
                            key=f"inp_{si}_{sbi}",
                            label_visibility="collapsed",
                        )
                    with col_btn:
                        checked = st.button("Check ✓", key=f"chk_{si}_{sbi}",
                                            type="primary")

                    if checked:
                        attempts = st.session_state.sv_attempts.get(key, 0) + 1
                        st.session_state.sv_attempts[key] = attempts

                        if abs(val - sub["ans"]) <= sub["tol"]:
                            # Correct
                            st.session_state.sv_done[key] = val
                            # Update live state
                            _solver_apply(si, sbi, val)
                            # XP
                            g = gs()
                            old = game.get_level_index(g["xp"])
                            g["xp"] += 10
                            if game.get_level_index(g["xp"]) > old:
                                st.balloons()
                            _save()

                            # Advance pointer
                            all_subs = len(step["sub"])
                            if sbi + 1 >= all_subs:
                                st.session_state.sv_step = si + 1
                                st.session_state.sv_sub  = 0
                            else:
                                st.session_state.sv_sub = sbi + 1
                            st.rerun()
                        else:
                            st.error(
                                f"Not quite. Your answer: {val:+.2f} {sub['unit']}. "
                                f"Expected ≈ {sub['ans']:+.2f} {sub['unit']}."
                            )
                            if attempts >= 2:
                                st.session_state.sv_show_hint[key] = True
                                st.rerun()
                    break  # only show one sub-step at a time within active step

                # Completed step summary
                if is_done:
                    for sbi, sub in enumerate(step["sub"]):
                        key = (si, sbi)
                        v = st.session_state.sv_done.get(key, sub["ans"])


def _solver_apply(si: int, sbi: int, val: float):
    """Store solved value into the live reaction/force dicts."""
    step = slv.STEPS[si]
    sub  = step["sub"][sbi]
    sid  = sub["id"]
    # Reactions
    if sid in ("Ax", "Ay", "By"):
        st.session_state.sv_reactions[sid] = val
    # Member forces (use the exact answer, not the student's val, for display)
    elif sid in slv.MEMBER_NAMES or sid.lstrip("F").replace("_", "") in [m.replace("_","") for m in slv.MEMBER_NAMES]:
        # map FAD → AD, FAC → AC, etc.
        name = sid.replace("F", "").replace("_", "")
        # Normalise: FAD → AD
        for mn in slv.MEMBER_NAMES:
            if mn.replace("_", "") == name or sid == "F" + mn or sid == "F_" + mn or sid == "F" + mn.replace("_",""):
                st.session_state.sv_forces[mn] = slv.SOLUTION[mn]
                break


# ── Direct Stiffness Method ───────────────────────────────────────────────────

def page_dsm():
    st.title("🧮 Direct Stiffness Method")
    st.markdown(
        "The **Direct Stiffness Method (DSM)** assembles a global stiffness matrix **[K]**, "
        "applies boundary conditions, and solves **[K]{d} = {F}** for nodal displacements. "
        "Member forces follow by back-substitution. Unlike the classical methods, "
        "it is systematic and computer-friendly."
    )

    tab1, tab2, tab3 = st.tabs(["📐 Problem Setup", "🔢 Step-by-Step", "🎛️ Interactive"])

    # ── Tab 1: Setup ──────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Example Truss")
        c1, c2 = st.columns([1.2, 1])
        with c1:
            fig = diagrams.diagram_dsm_nodes()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with c2:
            st.markdown("""
**Given**
- Node 1: (0, 0) — pin support
- Node 2: (4, 0) — pin support
- Node 3: (2, 2) — free, load **P ↓**
- Members: 1–3, 2–3
- Each member: stiffness **k = EA/L**

**Find**
- Displacement at node 3: u₃, v₃
- Axial force in each member

**Degrees of Freedom**
| DOF | Node | Dir | BC |
|-----|------|-----|----|
| 1   | 1    | →   | = 0 (pin) |
| 2   | 1    | ↑   | = 0 (pin) |
| 3   | 2    | →   | = 0 (pin) |
| 4   | 2    | ↑   | = 0 (pin) |
| 5   | 3    | →   | **free** |
| 6   | 3    | ↑   | **free** |
""")

    # ── Tab 2: Step-by-Step ───────────────────────────────────────────────────
    with tab2:
        res = dsm_solver.solve(EA_L=1000.0, P=10.0)

        with st.expander("Step 1 — Local stiffness matrix (bar element)", expanded=True):
            st.markdown(r"""
For a bar element from node **i** to node **j** with angle **θ**, length **L**, stiffness **k = EA/L**:

$$k_e = k \begin{bmatrix} c^2 & cs & -c^2 & -cs \\ cs & s^2 & -cs & -s^2 \\ -c^2 & -cs & c^2 & cs \\ -cs & -s^2 & cs & s^2 \end{bmatrix}$$

where $c = \cos\theta$, $s = \sin\theta$. The DOF order is $[u_i,\, v_i,\, u_j,\, v_j]$.
""")
            for md in res["member_data"]:
                st.markdown(f"**Member {md['member']}** — angle {md['angle']}°,  "
                            f"c = {md['c']},  s = {md['s']}")
                df = dsm_solver.element_ke_df(md["ke"] / 1000.0, md["dofs"])
                st.caption(f"kₑ / k  (DOFs: {md['dofs']})")
                st.dataframe(df, use_container_width=False)

        with st.expander("Step 2 — Assemble global stiffness matrix K"):
            st.markdown(
                "Each element's 4×4 matrix is scattered into the 6×6 global **K** "
                "at the rows/columns corresponding to the element's DOFs."
            )
            df_K = dsm_solver.k_matrix_df(res["K"] / 1000.0)
            st.caption("Global K / k  (6×6)")
            st.dataframe(df_K, use_container_width=False)

        with st.expander("Step 3 — Apply boundary conditions"):
            st.markdown(
                "Pin supports at nodes 1 and 2 → DOFs 1–4 = 0.  \n"
                "Delete the corresponding rows and columns to get the **reduced system**:"
            )
            df_Kred = pd.DataFrame(
                res["K_red"] / 1000.0,
                index=["u₃", "v₃"], columns=["u₃", "v₃"]
            ).round(3)
            st.caption("K_reduced / k")
            st.dataframe(df_Kred, use_container_width=False)
            st.markdown(
                r"$\mathbf{F}_{red} = \begin{bmatrix} 0 \\ -P \end{bmatrix}$"
            )

        with st.expander("Step 4 — Solve for displacements"):
            st.markdown(
                r"$\mathbf{K}_{red}\,\mathbf{d}_{free} = \mathbf{F}_{red}$"
            )
            st.markdown(
                r"By symmetry the off-diagonal of **K_red** is zero, so the system "
                r"decouples:"
            )
            st.markdown(
                f"""
$$u_3 = 0 \\quad\\text{{(by symmetry)}}$$

$$v_3 = \\frac{{-P}}{{k}} = \\frac{{-10}}{{1000}} = {res['v3']:.5f}\\text{{ m}}$$
"""
            )

        with st.expander("Step 5 — Member forces"):
            st.markdown(
                r"$F_{member} = k\,[c\,(u_j - u_i) + s\,(v_j - v_i)]$"
            )
            df_f = pd.DataFrame(res["member_forces"])
            st.dataframe(df_f, use_container_width=False, hide_index=True)

        with st.expander("Step 6 — Support reactions (verification)"):
            st.markdown(r"$\mathbf{R} = \mathbf{K}\,\mathbf{d}$")
            st.json(res["reactions"])

    # ── Tab 3: Interactive ────────────────────────────────────────────────────
    with tab3:
        st.markdown("Adjust the parameters and see results update in real time.")

        co1, co2 = st.columns(2)
        with co1:
            P    = st.slider("Applied load P (kN)", 1.0, 100.0, 10.0, 1.0)
            EA_L = st.select_slider(
                "Member stiffness k = EA/L (kN/m)",
                options=[100, 500, 1000, 2000, 5000, 10000],
                value=1000,
            )

        res_i = dsm_solver.solve(EA_L=float(EA_L), P=P)
        v3_mm = res_i["v3"] * 1000.0  # convert to mm

        with co2:
            st.metric("Vertical displacement v₃",
                      f"{v3_mm:.4f} mm",
                      delta=f"↓ {abs(v3_mm):.4f} mm")
            st.metric("Horizontal displacement u₃", "0.000 mm",
                      help="Zero by symmetry")

        st.write("")
        mc1, mc2 = st.columns(2)
        for col, mf in zip([mc1, mc2], res_i["member_forces"]):
            f   = mf["force_kN"]
            typ = mf["type"]
            col.metric(
                f"Force in member {mf['member']}",
                f"{f:.3f} kN",
                delta=typ,
                delta_color="off" if typ == "Zero" else (
                    "inverse" if typ == "Compression" else "normal"),
            )

        st.write("")
        fig_d = diagrams.diagram_dsm_deformed(v3_mm, scale=80.0 * 10.0 / max(abs(v3_mm), 0.001))
        st.pyplot(fig_d, use_container_width=True)
        plt.close(fig_d)


# ── Quiz menu ─────────────────────────────────────────────────────────────────

def page_quiz_menu():
    st.title("⚔️ Challenge — Quiz")
    topics = sorted({q["topic"] for q in QUESTIONS})
    c1, c2 = st.columns([1, 2])
    with c1:
        mode = st.radio("Quiz mode:", ["All topics"] + topics)
    with c2:
        n = len(QUESTIONS) if mode == "All topics" else sum(1 for q in QUESTIONS if q["topic"] == mode)
        st.metric("Questions", n)
        st.markdown("**XP rewards:**\n- ✅ Correct answer: +20 XP\n"
                    "- 🔥 Streak ×3: +10 bonus\n- ⚡ Streak ×5: +20 bonus\n"
                    "- 🏅 Perfect quiz: +50 bonus")
    if st.button("▶ Start Quiz", type="primary"):
        pool = QUESTIONS[:] if mode == "All topics" else [q for q in QUESTIONS if q["topic"] == mode]
        random.shuffle(pool)
        st.session_state.update(
            quiz_pool=pool, quiz_idx=0, quiz_score=0, quiz_wrong=[],
            quiz_answered=False, quiz_selected=None, quiz_topic=mode, streak=0)
        go("quiz_question")


def page_quiz_question():
    pool = st.session_state.quiz_pool
    idx  = st.session_state.quiz_idx
    if pool is None or idx >= len(pool):
        go("quiz_results")

    q        = pool[idx]
    answered = st.session_state.quiz_answered
    selected = st.session_state.quiz_selected
    streak   = st.session_state.streak

    h1, h2, h3 = st.columns([3, 1, 1])
    with h1:
        st.progress(idx / len(pool), text=f"Q {idx+1}/{len(pool)}")
    with h2:
        st.metric("Score", f"{st.session_state.quiz_score}/{idx}")
    with h3:
        if streak >= 5:
            st.markdown(f'<div class="streak-pill">⚡ {streak}</div>', unsafe_allow_html=True)
        elif streak >= 3:
            st.markdown(f'<div class="streak-pill">🔥 {streak}</div>', unsafe_allow_html=True)

    st.markdown(f"### Q{idx+1}. {q['question']}")
    st.caption(f"Topic: **{q['topic']}**")
    st.write("")

    for i, opt in enumerate(q["options"]):
        if answered:
            if   i == q["answer"]: st.success(f"✅  {opt}")
            elif i == selected:    st.error(f"❌  {opt}")
            else:                  st.button(opt, key=f"opt_{i}", disabled=True)
        else:
            if st.button(opt, key=f"opt_{i}", use_container_width=True):
                _handle_answer(i, q); st.rerun()

    if answered:
        st.write("")
        if selected == q["answer"]:
            xp = 20 + (20 if streak >= 5 else 10 if streak >= 3 else 0)
            st.success(f"**Correct! +{xp} XP**")
        else:
            st.error(f"**Incorrect.** Correct answer: *{q['options'][q['answer']]}*")
        st.info(f"💡 {q['explanation']}")
        is_last = idx + 1 >= len(pool)
        if st.button("🏁 See Results" if is_last else "Next →", type="primary"):
            st.session_state.quiz_idx      = idx + 1
            st.session_state.quiz_answered = False
            st.session_state.quiz_selected = None
            if is_last:
                _finish_quiz()
            st.rerun()


def _handle_answer(sel, q):
    g       = gs()
    correct = sel == q["answer"]
    st.session_state.quiz_selected = sel
    st.session_state.quiz_answered = True
    g["total_answered"] += 1
    if correct:
        st.session_state.quiz_score      += 1
        st.session_state.streak          += 1
        g["total_correct"]               += 1
        xp = 20 + (20 if st.session_state.streak >= 5 else
                   10 if st.session_state.streak >= 3 else 0)
        old = game.get_level_index(g["xp"])
        g["xp"] += xp
        if game.get_level_index(g["xp"]) > old:
            st.balloons()
    else:
        st.session_state.quiz_wrong.append(q)
        st.session_state.streak = 0
    if st.session_state.streak > g["best_streak"]:
        g["best_streak"] = st.session_state.streak
    _save()


def _finish_quiz():
    g = gs()
    if st.session_state.quiz_score == len(st.session_state.quiz_pool):
        old = game.get_level_index(g["xp"])
        g["xp"] += 50
        if game.get_level_index(g["xp"]) > old:
            st.balloons()
    new_a = game.check_achievements(
        g, st.session_state.streak,
        st.session_state.quiz_topic, len(st.session_state.quiz_pool))
    st.session_state.toasts.extend(new_a)
    _save()


def page_quiz_results():
    g     = gs()
    pool  = st.session_state.quiz_pool or []
    score = st.session_state.quiz_score
    total = len(pool)
    wrong = st.session_state.quiz_wrong
    pct   = score / total * 100 if total else 0

    st.title("📊 Quiz Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score",       f"{score}/{total}")
    c2.metric("Percentage",  f"{pct:.0f}%")
    c3.metric("Incorrect",   len(wrong))
    c4.metric("Best Streak", f"{g['best_streak']} 🔥")
    st.progress(score / total if total else 0)

    if   pct == 100: st.success("🎉 Perfect! +50 bonus XP awarded.")
    elif pct >= 75:  st.success("👍 Great work!")
    elif pct >= 50:  st.warning("📚 Keep practising — review the tutorials below.")
    else:            st.error("🔁 More study needed. Head back to Learn.")

    if wrong:
        seen = set()
        for q in wrong:
            if q["topic"] not in seen:
                st.markdown(f"- 📖 **{q['topic']}**"); seen.add(q["topic"])

    ca, cb, cc = st.columns(3)
    if ca.button("🔁 Retry",        use_container_width=True):
        pool2 = st.session_state.quiz_pool[:]
        random.shuffle(pool2)
        st.session_state.update(quiz_pool=pool2, quiz_idx=0, quiz_score=0,
            quiz_wrong=[], quiz_answered=False, quiz_selected=None, streak=0)
        go("quiz_question")
    if cb.button("📝 New Quiz",     use_container_width=True): go("quiz_menu")
    if cc.button("📖 Tutorials",    use_container_width=True): go("tutorials")


# ── Achievements ──────────────────────────────────────────────────────────────

def page_achievements():
    g        = gs()
    unlocked = set(g["unlocked"])
    st.title("🏅 Achievements")
    st.caption(f"{len(unlocked)} / {len(game.ACHIEVEMENTS)} unlocked")
    st.write("")
    cols = st.columns(2)
    for i, ach in enumerate(game.ACHIEVEMENTS):
        is_u = ach["id"] in unlocked
        cls  = "ach-card unlocked" if is_u else "ach-card locked"
        stat = "✅ Unlocked" if is_u else f"🔒 +{ach['xp']} XP on unlock"
        fc   = "#0f172a" if is_u else "#94a3b8"
        with cols[i % 2]:
            st.markdown(
                f'<div class="{cls}"><span style="font-size:1.7em">{ach["icon"]}</span> '
                f'<strong style="color:{fc}"> {ach["name"]}</strong><br>'
                f'<span style="color:#64748b;font-size:0.87em">{ach["desc"]}</span><br>'
                f'<span style="color:{"#16a34a" if is_u else "#64748b"};font-size:0.82em">{stat}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── Reference ─────────────────────────────────────────────────────────────────

def page_reference():
    st.title("📋 Quick Reference")

    st.subheader("Determinacy")
    st.markdown("""
| Condition | Classification |
|-----------|---------------|
| m + r = 2j | ✅ Statically determinate |
| m + r < 2j | ❌ Unstable (mechanism) |
| m + r > 2j | ⚠️ Statically indeterminate |
""")
    st.caption("m = members · r = reaction components · j = joints")

    st.subheader("Method of Joints")
    st.markdown("""
| Rule | Detail |
|------|--------|
| Equations per joint | ΣFx = 0 and ΣFy = 0 |
| Starting joint | ≤ 2 unknown members |
| Convention | Assume tension; negative result → compression |
| Zero-force A | 2 non-collinear members, no load → both zero |
| Zero-force B | 3 members, 2 collinear, no load → third is zero |
""")

    st.subheader("Method of Sections")
    st.markdown("""
| Rule | Detail |
|------|--------|
| Equations | ΣFx = 0, ΣFy = 0, ΣM = 0 |
| Cut limit | ≤ 3 unknown members per cut |
| Moment point | Intersection of the other two unknowns |
""")

    st.subheader("Direct Stiffness Method")
    st.markdown(r"""
| Step | Formula |
|------|---------|
| Element stiffness (local) | $k_e = \frac{EA}{L}\begin{bmatrix}1&-1\\-1&1\end{bmatrix}$ |
| Global element matrix | $\mathbf{K}_e = \mathbf{T}^T k_e \mathbf{T}$ |
| Global assembly | $\mathbf{K} = \sum \mathbf{K}_e$ |
| Solve | $\mathbf{K}_{red}\,\mathbf{d} = \mathbf{F}_{red}$ |
| Member force | $F = \frac{EA}{L}[c(u_j-u_i)+s(v_j-v_i)]$ |
""")

    st.subheader("Truss Types")
    fig = diagrams.diagram_truss_types()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ── Router ────────────────────────────────────────────────────────────────────

{
    "home":         page_home,
    "tutorials":    page_tutorials,
    "solve":        page_solve,
    "dsm":          page_dsm,
    "quiz_menu":    page_quiz_menu,
    "quiz_question":page_quiz_question,
    "quiz_results": page_quiz_results,
    "achievements": page_achievements,
    "reference":    page_reference,
}.get(st.session_state.page, page_home)()
