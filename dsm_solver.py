"""
Direct Stiffness Method for a simple 2-member symmetric truss.

Problem
-------
        3  (P ↓)
       / \\
      /   \\
     /     \\
    1-------2
   pin     pin

Node 1: (0, 0) — pin
Node 2: (4, 0) — pin
Node 3: (2, 2) — free, loaded P downward

Members: 1-3 and 2-3, each with stiffness k = EA/L.

Closed-form solution
--------------------
By symmetry the reduced system is diagonal:
  K_red = k * [[1, 0], [0, 1]]   (DOFs: u3, v3)
  u3 = 0
  v3 = -P / k
  F_13 = F_23 = -P / sqrt(2)  (compression)
"""

import numpy as np
import pandas as pd


def _member_ke(xi, yi, xj, yj, k):
    """4×4 global element stiffness for a bar."""
    L  = np.hypot(xj - xi, yj - yi)
    c  = (xj - xi) / L
    s  = (yj - yi) / L
    m  = np.array([[c*c, c*s, -c*c, -c*s],
                   [c*s, s*s, -c*s, -s*s],
                   [-c*c, -c*s, c*c, c*s],
                   [-c*s, -s*s, c*s, s*s]])
    return k * m, c, s


def solve(EA_L: float = 1000.0, P: float = 10.0):
    """
    Returns a dict with everything needed for display.
    EA_L : EA/L for each member [kN/m or normalised]
    P    : downward load at node 3 [kN]
    """
    nodes   = {1: (0.0, 0.0), 2: (4.0, 0.0), 3: (2.0, 2.0)}
    members = [(1, 3), (2, 3)]

    # ── Build 6×6 global K ────────────────────────────────────────────────────
    K = np.zeros((6, 6))
    member_data = []

    for i_n, j_n in members:
        xi, yi = nodes[i_n]
        xj, yj = nodes[j_n]
        ke, c, s = _member_ke(xi, yi, xj, yj, EA_L)
        L = np.hypot(xj - xi, yj - yi)
        angle_deg = float(np.degrees(np.arctan2(yj - yi, xj - xi)))

        dofs = [2*(i_n-1), 2*(i_n-1)+1, 2*(j_n-1), 2*(j_n-1)+1]
        for a, da in enumerate(dofs):
            for b, db in enumerate(dofs):
                K[da, db] += ke[a, b]

        member_data.append({
            "member": f"{i_n}–{j_n}",
            "L":      round(L, 4),
            "angle":  round(angle_deg, 2),
            "c":      round(c, 4),
            "s":      round(s, 4),
            "ke":     ke,
            "dofs":   [d+1 for d in dofs],  # 1-indexed for display
        })

    # ── BCs: nodes 1 and 2 are pinned → DOFs 0,1,2,3 = 0 ────────────────────
    free = [4, 5]  # u3 (DOF 5), v3 (DOF 6) — 0-indexed
    K_red = K[np.ix_(free, free)]
    F_red = np.array([0.0, -P])

    # ── Solve ─────────────────────────────────────────────────────────────────
    d_free = np.linalg.solve(K_red, F_red)
    d = np.zeros(6)
    d[free] = d_free

    # ── Member forces ──────────────────────────────────────────────────────────
    member_forces = []
    for idx, (i_n, j_n) in enumerate(members):
        xi, yi = nodes[i_n]
        xj, yj = nodes[j_n]
        L  = np.hypot(xj - xi, yj - yi)
        c  = (xj - xi) / L
        s  = (yj - yi) / L
        di = d[2*(i_n-1):2*(i_n-1)+2]
        dj = d[2*(j_n-1):2*(j_n-1)+2]
        F  = EA_L * (c*(dj[0]-di[0]) + s*(dj[1]-di[1]))
        member_forces.append({
            "member":  f"{i_n}–{j_n}",
            "force_kN": round(F, 4),
            "type":    "Compression" if F < -1e-9 else ("Tension" if F > 1e-9 else "Zero"),
        })

    # ── Reaction forces ────────────────────────────────────────────────────────
    reactions = K @ d
    reaction_table = {
        "R1x (kN)": round(reactions[0], 4),
        "R1y (kN)": round(reactions[1], 4),
        "R2x (kN)": round(reactions[2], 4),
        "R2y (kN)": round(reactions[3], 4),
    }

    return {
        "nodes":          nodes,
        "members":        members,
        "K":              K,
        "K_red":          K_red,
        "F_red":          F_red,
        "d":              d,
        "u3":             round(d[4], 6),
        "v3":             round(d[5], 6),
        "member_data":    member_data,
        "member_forces":  member_forces,
        "reactions":      reaction_table,
        "EA_L":           EA_L,
        "P":              P,
    }


# ── Display helpers ────────────────────────────────────────────────────────────

def k_matrix_df(K: np.ndarray) -> pd.DataFrame:
    labels = ["u₁", "v₁", "u₂", "v₂", "u₃", "v₃"]
    df = pd.DataFrame(K, index=labels, columns=labels)
    return df.round(3)


def element_ke_df(ke: np.ndarray, dofs: list[int]) -> pd.DataFrame:
    lbl = [f"DOF {d}" for d in dofs]
    return pd.DataFrame(ke, index=lbl, columns=lbl).round(3)
