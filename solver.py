"""
Step-by-step interactive solver for a 5-member symmetric truss.

Problem
-------
        D  (40 kN ↓)
       /|\\
      / | \\
     /  |  \\
    A---C---B
   pin      roller

Joints : A(0,0)  B(4,0)  C(2,0)  D(2,2)
Members: AC  CB  AD  BD  CD
Load   : 40 kN ↓ at D
Answer : Ax=0  Ay=20  By=20
         F_AC=+20(T)  F_CB=+20(T)
         F_AD=-28.28(C)  F_BD=-28.28(C)  F_CD=0
"""

import numpy as np

# ── Geometry ─────────────────────────────────────────────────────────────────

JOINTS = {
    "A": np.array([0.0, 0.0]),
    "B": np.array([4.0, 0.0]),
    "C": np.array([2.0, 0.0]),
    "D": np.array([2.0, 2.0]),
}

MEMBERS = [("A", "C"), ("C", "B"), ("A", "D"), ("B", "D"), ("C", "D")]
MEMBER_NAMES = ["AC", "CB", "AD", "BD", "CD"]
LOAD_KN = 40.0

SOLUTION = {
    "Ax": 0.0, "Ay": 20.0, "By": 20.0,
    "AC": 20.0, "CB": 20.0,
    "AD": -20.0 * np.sqrt(2), "BD": -20.0 * np.sqrt(2),
    "CD": 0.0,
}

# ── Step definitions ──────────────────────────────────────────────────────────
# Each step has sub-questions; student types a numerical answer.

STEPS = [
    {
        "id":    "reactions",
        "title": "Step 1 — Global Equilibrium (Support Reactions)",
        "icon":  "⚖️",
        "intro": (
            "Before analysing any joint, find the **three support reactions** "
            "by applying equilibrium to the entire truss: ΣFx = 0, ΣFy = 0, ΣM = 0. "
            "Tip: take moments about A to find By first."
        ),
        "highlight": None,
        "sub": [
            {
                "id":    "Ax",
                "label": "Horizontal reaction at A — find **Ax** (kN)",
                "eq":    "ΣFx = 0 :   Ax  =  ?",
                "hint":  "There are no horizontal external forces on the truss.",
                "ans":   0.0,
                "tol":   0.1,
                "unit":  "kN",
                "expl":  "No horizontal loads ⟹ **Ax = 0 kN**.",
            },
            {
                "id":    "By",
                "label": "Vertical reaction at B — find **By** (kN)",
                "eq":    "ΣM_A = 0 :   By × 4  −  40 × 2  =  0   ⟹  By = ?",
                "hint":  "Moments about A: the 40 kN load acts at x = 2 m, By acts at x = 4 m.",
                "ans":   20.0,
                "tol":   0.5,
                "unit":  "kN",
                "expl":  "ΣM_A = 0 : By × 4 = 40 × 2 → **By = 20 kN ↑**.",
            },
            {
                "id":    "Ay",
                "label": "Vertical reaction at A — find **Ay** (kN)",
                "eq":    "ΣFy = 0 :   Ay  +  By  −  40  =  0   ⟹  Ay = ?",
                "hint":  "You already know By.",
                "ans":   20.0,
                "tol":   0.5,
                "unit":  "kN",
                "expl":  "ΣFy = 0 : Ay = 40 − 20 → **Ay = 20 kN ↑**.",
            },
        ],
    },
    {
        "id":    "joint_A",
        "title": "Step 2 — Method of Joints at A",
        "icon":  "🔵",
        "intro": (
            "Joint A has **two unknown members**: AD and AC. "
            "Assume all unknowns are in **tension** (pulling away from the joint). "
            "A negative result will mean compression."
        ),
        "highlight": "A",
        "sub": [
            {
                "id":    "FAD",
                "label": "Force in member AD — find **F_AD** (kN, + = tension)",
                "eq":    (
                    "AD makes 45 ° with horizontal  (cos 45° = sin 45° = 0.707)\n"
                    "ΣFy = 0 :   Ay  +  F_AD × sin 45°  =  0\n"
                    "            20  +  F_AD × 0.707     =  0   ⟹  F_AD = ?"
                ),
                "hint":  "F_AD × 0.707 = −20  →  F_AD = −20 / 0.707",
                "ans":   -20.0 * np.sqrt(2),
                "tol":   0.5,
                "unit":  "kN",
                "expl":  "F_AD = −20/0.707 = **−28.28 kN (Compression)**.",
            },
            {
                "id":    "FAC",
                "label": "Force in member AC — find **F_AC** (kN, + = tension)",
                "eq":    (
                    "ΣFx = 0 :   Ax  +  F_AC  +  F_AD × cos 45°  =  0\n"
                    "              0  +  F_AC  +  (−28.28)×0.707  =  0   ⟹  F_AC = ?"
                ),
                "hint":  "F_AC = +28.28 × 0.707",
                "ans":   20.0,
                "tol":   0.5,
                "unit":  "kN",
                "expl":  "F_AC = +28.28 × 0.707 = **+20 kN (Tension)**.",
            },
        ],
    },
    {
        "id":    "joint_B",
        "title": "Step 3 — Method of Joints at B",
        "icon":  "🔵",
        "intro": (
            "Joint B is symmetric to A. Unknown members: BD and CB. "
            "BD makes 135 ° with the +x axis "
            "(cos 135° = −0.707, sin 135° = +0.707)."
        ),
        "highlight": "B",
        "sub": [
            {
                "id":    "FBD",
                "label": "Force in member BD — find **F_BD** (kN, + = tension)",
                "eq":    (
                    "ΣFy = 0 :   By  +  F_BD × sin 135°  =  0\n"
                    "            20  +  F_BD × 0.707      =  0   ⟹  F_BD = ?"
                ),
                "hint":  "Same calculation as Step 2 for F_AD — symmetric truss.",
                "ans":   -20.0 * np.sqrt(2),
                "tol":   0.5,
                "unit":  "kN",
                "expl":  "F_BD = −20/0.707 = **−28.28 kN (Compression)**.",
            },
            {
                "id":    "FCB",
                "label": "Force in member CB — find **F_CB** (kN, + = tension)",
                "eq":    (
                    "ΣFx = 0 :   F_CB  +  F_BD × cos 135°  =  0\n"
                    "            F_CB  +  (−28.28)×(−0.707) =  0   ⟹  F_CB = ?"
                ),
                "hint":  "cos 135° = −0.707, so the x-component of F_BD is positive.",
                "ans":   20.0,
                "tol":   0.5,
                "unit":  "kN",
                "expl":  "F_CB = −(−28.28 × −0.707) = **+20 kN (Tension)**.",
            },
        ],
    },
    {
        "id":    "joint_C",
        "title": "Step 4 — Method of Joints at C (Zero-Force Check)",
        "icon":  "⭕",
        "intro": (
            "Joint C has three members: CA, CB, CD — and **no external load**. "
            "Two of them (CA and CB) are collinear (both horizontal). "
            "Apply the zero-force-member rule, or verify with equilibrium."
        ),
        "highlight": "C",
        "sub": [
            {
                "id":    "FCD",
                "label": "Force in member CD — find **F_CD** (kN, + = tension)",
                "eq":    (
                    "Known: F_CA = −20 kN (i.e. force on C is +20 kN toward B)\n"
                    "       F_CB = +20 kN (force on C is +20 kN toward B)\n"
                    "CD is vertical (90°). ΣFy = 0 :   F_CD = ?"
                ),
                "hint":  (
                    "The two horizontal members perfectly balance each other in x. "
                    "Only F_CD can satisfy ΣFy = 0."
                ),
                "ans":   0.0,
                "tol":   0.1,
                "unit":  "kN",
                "expl":  (
                    "ΣFy = F_CD = 0 → **F_CD = 0 (Zero-force member)**. "
                    "This is a classic zero-force rule: 3 members at an unloaded joint, "
                    "2 collinear → the third (CD) carries zero force."
                ),
            },
        ],
    },
]

# ── Helpers used by main.py ───────────────────────────────────────────────────

def total_substeps():
    return sum(len(s["sub"]) for s in STEPS)


def substep_index(step_i: int, sub_i: int) -> int:
    idx = 0
    for si in range(step_i):
        idx += len(STEPS[si]["sub"])
    return idx + sub_i


def member_angle_deg(name: str) -> float:
    a, b = name[0], name[1]
    p1, p2 = JOINTS[a], JOINTS[b]
    dx, dy = p2 - p1
    return float(np.degrees(np.arctan2(dy, dx)))
