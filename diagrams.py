"""
Professional engineering-quality truss diagrams.
All diagrams use a clean white background and a consistent colour palette
that reads well in both screen and print contexts.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

# ── Colour palette ────────────────────────────────────────────────────────────
C_MBR   = "#1e3a5f"   # dark navy — generic member
C_TEN   = "#15803d"   # forest green — tension
C_CMP   = "#b91c1c"   # crimson — compression
C_ZERO  = "#d97706"   # amber — zero-force
C_UNK   = "#94a3b8"   # slate — unknown / unsolved member
C_JNT   = "#1d4ed8"   # blue — joint fill
C_SUP   = "#374151"   # dark grey — supports & hatching
C_LOAD  = "#92400e"   # brown — applied loads
C_RXN   = "#6d28d9"   # purple — reactions
C_DIM   = "#64748b"   # dim grey — dimension lines
C_BG    = "#ffffff"

plt.rcParams.update({
    "font.family":     "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  False,
    "axes.spines.bottom":False,
    "figure.facecolor":  C_BG,
    "axes.facecolor":    C_BG,
    "savefig.facecolor": C_BG,
})


# ── Low-level primitives ──────────────────────────────────────────────────────

def _ax_clean(ax):
    ax.set_facecolor(C_BG)
    ax.set_aspect("equal")
    ax.axis("off")


def _member(ax, p1, p2, color=C_MBR, lw=3.0, zorder=2, ls="-", alpha=1.0):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], ls,
            color=color, lw=lw, solid_capstyle="round",
            dash_capstyle="round", zorder=zorder, alpha=alpha)


def _joint(ax, x, y, r=0.09, label=None, off=(0, 0.17), fs=11,
           fc=C_JNT, label_color="#0f172a"):
    ax.add_patch(mpatches.Circle((x, y), r * 1.45, color="white",   zorder=5))
    ax.add_patch(mpatches.Circle((x, y), r,        color=fc,        zorder=6))
    ax.add_patch(mpatches.Circle((x, y), r * 0.42, color="white",   zorder=7))
    if label:
        ax.text(x + off[0], y + off[1], label, ha="center", va="bottom",
                fontsize=fs, fontweight="bold", color=label_color, zorder=8)


def _pin(ax, x, y, s=0.20):
    ax.add_patch(plt.Polygon(
        [(x, y), (x - s, y - s * 1.35), (x + s, y - s * 1.35)],
        color=C_SUP, zorder=1, linewidth=0))
    ax.plot([x - s * 1.4, x + s * 1.4], [y - s * 1.35, y - s * 1.35],
            color=C_SUP, lw=1.8, zorder=1)
    for i in range(6):
        xi = x - s * 1.2 + i * s * 0.48
        ax.plot([xi, xi - s * 0.22], [y - s * 1.35, y - s * 1.65],
                color=C_SUP, lw=1.0, zorder=1)


def _roller(ax, x, y, s=0.20):
    ax.add_patch(plt.Polygon(
        [(x, y), (x - s, y - s * 1.1), (x + s, y - s * 1.1)],
        color=C_SUP, zorder=1, linewidth=0))
    ax.add_patch(mpatches.Circle((x, y - s * 1.42), s * 0.28,
                                  color=C_SUP, fill=False, lw=1.8, zorder=1))
    ax.plot([x - s * 1.4, x + s * 1.4], [y - s * 1.72, y - s * 1.72],
            color=C_SUP, lw=1.8, zorder=1)


def _arrow(ax, ox, oy, dx, dy, color=C_LOAD, label="", lpad=(0.14, 0.0),
           head_scale=18, lw=2.0):
    ax.annotate("",
                xy=(ox + dx, oy + dy), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="->", color=color,
                                lw=lw, mutation_scale=head_scale),
                zorder=9)
    if label:
        ax.text(ox + dx / 2 + lpad[0],
                oy + dy / 2 + lpad[1],
                label, color=color, fontsize=10, fontweight="bold",
                ha="center", va="center", zorder=10)


def _dim(ax, p1, p2, text, offset=(0, -0.35)):
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="<->", color=C_DIM, lw=1.0,
                                mutation_scale=10), zorder=1)
    ax.text(mx + offset[0], my + offset[1], text,
            ha="center", va="center", fontsize=8, color=C_DIM, style="italic")


def _force_label(ax, x, y, text, color=C_MBR):
    ax.text(x, y, text, ha="center", va="center", fontsize=8,
            color=color, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, lw=0.8, alpha=0.9),
            zorder=11)


# ── 1. What is a Truss? ───────────────────────────────────────────────────────

def diagram_basic_truss():
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(C_BG)
    _ax_clean(ax)

    J = {"A": np.array([0.0, 0.0]),
         "B": np.array([4.0, 0.0]),
         "C": np.array([2.0, 2.4])}

    # Members
    for p, q, lbl, off in [
        ("A", "B", "Bottom Chord (AB)",     (2.0, -0.22)),
        ("A", "C", "Left Rafter (AC)",       (0.7, 1.3)),
        ("B", "C", "Right Rafter (BC)",      (3.3, 1.3)),
    ]:
        _member(ax, J[p], J[q])
        ax.text(*off, lbl, ha="center", va="center", fontsize=8.5,
                color="#334155", style="italic")

    # Joints
    _joint(ax, *J["A"], label="A", off=(0, -0.38))
    _joint(ax, *J["B"], label="B", off=(0, -0.38))
    _joint(ax, *J["C"], label="C", off=(0,  0.19))

    # Supports
    _pin(ax, *J["A"])
    _roller(ax, *J["B"])
    ax.text(0,  -0.80, "Pin support\n(Ax, Ay)", ha="center", fontsize=8.0, color="#64748b")
    ax.text(4,  -0.80, "Roller support\n(By only)", ha="center", fontsize=8.0, color="#64748b")

    # Load
    _arrow(ax, 2, 2.4, 0, -0.75, label="P", lpad=(0.16, 0))

    # Reactions
    _arrow(ax, 0, 0, 0,    0.65, color=C_RXN, label="Ay", lpad=(0.20, 0))
    _arrow(ax, 0, 0, 0.65, 0,    color=C_RXN, label="Ax", lpad=(0, 0.15))
    _arrow(ax, 4, 0, 0,    0.65, color=C_RXN, label="By", lpad=(0.20, 0))

    # Dimension lines
    _dim(ax, (0, 0), (4, 0), "4 m", offset=(0, -0.30))
    _dim(ax, (2, 0), (2, 2.4), "h", offset=(0.28, 0))

    # Info box
    ax.text(5.0, 1.2,
            "Ideal Truss\nAssumptions:\n\n"
            "• Members = 2-force\n"
            "• Joints = frictionless pins\n"
            "• Loads at joints only\n"
            "• m + r = 2j  (det.)",
            fontsize=8.5, va="center", color="#0f172a",
            bbox=dict(boxstyle="round,pad=0.55", fc="#eff6ff",
                      ec="#2563eb", lw=1.2))

    ax.set_xlim(-1.0, 6.4)
    ax.set_ylim(-1.2, 3.5)
    ax.set_title("Simple Triangular Truss — Joints, Members & Reactions",
                 fontsize=13, fontweight="bold", color="#0f172a", pad=10)
    plt.tight_layout()
    return fig


# ── 2. Types of Trusses ───────────────────────────────────────────────────────

def diagram_truss_types():
    configs = [
        ("Pratt",  True,  [(0, 5), (1, 6), (2, 7)],
         "Diagonals in tension\nVerticals in compression"),
        ("Warren", False, [(0, 5), (1, 4), (2, 5), (3, 6)],  # adjusted for no-vert
         "No verticals\nAlternating diagonals"),
        ("Howe",   True,  [(4, 1), (5, 2), (6, 3)],
         "Diagonals in compression\nVerticals in tension"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    fig.patch.set_facecolor(C_BG)

    for ax, (title, has_vert, diags, note) in zip(axes, configs):
        _ax_clean(ax)
        B = [(i, 0.0) for i in range(4)]
        T = [(i, 1.0) for i in range(4)]

        # Chords (navy)
        for i in range(3):
            _member(ax, B[i], B[i+1])
            _member(ax, T[i], T[i+1])

        # Verticals (slate)
        if has_vert:
            for i in range(4):
                _member(ax, B[i], T[i], color="#475569", lw=2.2)

        # Diagonals
        for src, dst in diags:
            if src < 4:
                p1, p2 = B[src], T[dst - 4]
            else:
                p1, p2 = T[src - 4], B[dst]
            _member(ax, p1, p2, color=C_TEN, lw=2.4)

        # Joints
        for x, y in B + T:
            _joint(ax, x, y, r=0.07)

        _pin(ax,   0, 0, s=0.13)
        _roller(ax, 3, 0, s=0.13)

        ax.set_xlim(-0.5, 3.6)
        ax.set_ylim(-0.55, 1.55)
        ax.set_title(f"{title} Truss", fontsize=12, fontweight="bold",
                     color="#0f172a", pad=6)
        ax.text(1.5, -0.44, note, ha="center", fontsize=7.5,
                color="#475569", style="italic")

    plt.tight_layout(pad=1.2)
    return fig


# ── 3. Method of Joints ───────────────────────────────────────────────────────

def diagram_method_joints():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor(C_BG)

    # Left — full 3-panel truss
    B = [(i, 0.0) for i in range(4)]
    T = [(i, 1.0) for i in range(4)]
    _ax_clean(ax1)

    for i in range(3):
        _member(ax1, B[i], B[i+1])
        _member(ax1, T[i], T[i+1])
    for i in range(4):
        _member(ax1, B[i], T[i], color="#64748b", lw=2.0)
    for src, dst in [(0, 5), (1, 6), (2, 7)]:
        _member(ax1, B[src], T[dst-4], color="#64748b", lw=2.0)

    for i, (x, y) in enumerate(B):
        _joint(ax1, x, y, r=0.07, label=str(i+1), off=(0, -0.28), fs=9)
    for i, (x, y) in enumerate(T):
        _joint(ax1, x, y, r=0.07, label=chr(65+i), fs=9)

    _pin(ax1, 0, 0, s=0.14)
    _roller(ax1, 3, 0, s=0.14)
    _arrow(ax1, 1, 1, 0, -0.5, label="P")
    _arrow(ax1, 2, 1, 0, -0.5, label="P")

    # Highlight joint A (top-left)
    ax1.add_patch(mpatches.Circle((0, 1), 0.26, color="#fbbf24",
                                   fill=False, lw=2.5, ls="--", zorder=8))
    ax1.text(0, 1.45, "Analyse\nthis joint", ha="center", fontsize=8.5,
             color="#b45309", fontweight="bold")

    ax1.set_xlim(-0.6, 4.2)
    ax1.set_ylim(-0.75, 2.0)
    ax1.set_title("Identify a joint with ≤ 2 unknowns", fontsize=11,
                  fontweight="bold", color="#0f172a", pad=8)

    # Right — FBD of joint A
    _ax_clean(ax2)
    ox, oy = 1.7, 1.5

    # Joint circle
    ax2.add_patch(mpatches.Circle((ox, oy), 0.22, color="#fef3c7",
                                   ec="#f59e0b", lw=2.0, zorder=5))
    ax2.text(ox, oy, "A", ha="center", va="center", fontsize=13,
             fontweight="bold", color="#0f172a", zorder=6)

    _arrow(ax2, ox, oy,  0.90,  0,    color=C_TEN,  label="F_AB → (T)",  lpad=(0, 0.20))
    _arrow(ax2, ox, oy,  0.65, -0.65, color=C_CMP,  label="F_A1 (C)",    lpad=(0.50, 0.10))
    _arrow(ax2, ox, oy,  0,    0.85,  color=C_RXN,  label="Ay ↑",        lpad=(0.28, 0))
    _arrow(ax2, ox, oy,  0.80,  0,    color=C_RXN,  label="Ax →",        lpad=(0, -0.20))

    ax2.text(ox, oy - 0.70,
             "ΣFx = 0 :  Ax + F_AB cosθ  = 0\n"
             "ΣFy = 0 :  Ay + F_A1 sinθ  = 0",
             ha="center", fontsize=9, color="#0f172a",
             bbox=dict(boxstyle="round,pad=0.45", fc="#dbeafe",
                       ec="#3b82f6", lw=1.2))

    ax2.set_xlim(0.2, 3.5)
    ax2.set_ylim(0.3, 3.0)
    ax2.set_title("Free-Body Diagram at Joint A", fontsize=11,
                  fontweight="bold", color="#0f172a", pad=8)

    plt.tight_layout(pad=1.2)
    return fig


# ── 4. Method of Sections ─────────────────────────────────────────────────────

def diagram_method_sections():
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(C_BG)
    _ax_clean(ax)

    B = [(i, 0.0) for i in range(5)]
    T = [(i, 1.0) for i in range(5)]
    CUT_X = 1.6  # cut between panels 1 and 2

    # Draw members — grey out "right of cut"
    for i in range(4):
        fade = i >= 2
        _member(ax, B[i], B[i+1], color="#cbd5e1" if fade else C_MBR, alpha=0.5 if fade else 1.0)
        _member(ax, T[i], T[i+1], color="#cbd5e1" if fade else C_MBR, alpha=0.5 if fade else 1.0)
    for i in range(5):
        fade = i >= 2
        _member(ax, B[i], T[i],   color="#cbd5e1" if fade else "#64748b", alpha=0.5 if fade else 1.0)
    for src, dst in [(0, 5), (1, 6), (2, 7), (3, 8)]:
        fade = src >= 2
        _member(ax, B[src], T[dst-4], color="#cbd5e1" if fade else "#64748b", alpha=0.5 if fade else 1.0)

    # Highlight the 3 cut members in red
    _member(ax, T[1], T[2], color=C_CMP, lw=3.8)   # F₁ — top chord
    _member(ax, B[1], T[2], color=C_ZERO, lw=3.8)  # F₂ — diagonal
    _member(ax, B[1], B[2], color=C_TEN, lw=3.8)   # F₃ — bottom chord

    for x, y in B + T:
        _joint(ax, x, y, r=0.07)

    _pin(ax,   0, 0, s=0.13)
    _roller(ax, 4, 0, s=0.13)
    _arrow(ax, 2, 1, 0, -0.5, label="P")
    _arrow(ax, 0, 0, 0,  0.55, color=C_RXN, label="Ay")
    _arrow(ax, 4, 0, 0,  0.55, color=C_RXN, label="By")

    # Cut plane
    ax.axvline(CUT_X, ymin=0.05, ymax=0.95, color=C_CMP, lw=2.0, ls="--", zorder=9)
    ax.text(CUT_X, -0.48, "Cut", ha="center", fontsize=9,
            color=C_CMP, fontweight="bold")

    # Force labels on cut members
    _force_label(ax, 1.3, 1.12, "F₁ (top chord)", C_CMP)
    _force_label(ax, 1.0, 0.55, "F₂ (diagonal)", C_ZERO)
    _force_label(ax, 1.3, -0.13, "F₃ (bot chord)", C_TEN)

    # Equations
    ax.text(3.6, 0.50,
            "Take left section:\n\n"
            "ΣFx = 0\nΣFy = 0\nΣM = 0\n\n→ Solve F₁, F₂, F₃",
            fontsize=9, color="#0f172a", va="center", ha="center",
            bbox=dict(boxstyle="round,pad=0.5", fc="#fefce8",
                      ec="#ca8a04", lw=1.2))

    ax.set_xlim(-0.5, 5.0)
    ax.set_ylim(-0.85, 1.85)
    ax.set_title("Method of Sections — Cut Through ≤ 3 Members",
                 fontsize=13, fontweight="bold", color="#0f172a", pad=10)
    plt.tight_layout()
    return fig


# ── 5. Determinacy ────────────────────────────────────────────────────────────

def diagram_determinacy():
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    fig.patch.set_facecolor(C_BG)

    cases = [
        ("#16a34a", "Statically\nDeterminate",  "m + r = 2j\n7 + 3 = 10 ✓", False, False),
        ("#d97706", "Statically\nIndeterminate", "m + r > 2j\n8 + 3 > 10",   True,  False),
        ("#dc2626", "Unstable\n(Mechanism)",     "m + r < 2j\n6 + 3 < 10",   False, True),
    ]

    for ax, (color, title, note, add_member, rm_member) in zip(axes, cases):
        _ax_clean(ax)
        B = [(0, 0), (1, 0), (2, 0)]
        T = [(0.5, 1), (1.5, 1)]
        base = [(B[0], B[1]), (B[1], B[2]),
                (B[0], T[0]), (B[1], T[0]), (B[1], T[1]),
                (B[2], T[1]), (T[0], T[1])]

        members = base[:]
        if add_member:
            members.append((B[0], T[1]))
        if rm_member:
            members = [m for m in members if m != (B[1], T[1])]

        for p, q in members:
            _member(ax, p, q, color=C_MBR, lw=2.2)

        for x, y in B:
            _joint(ax, x, y, r=0.06)
        for x, y in T:
            _joint(ax, x, y, r=0.06)

        if add_member:
            _member(ax, B[0], T[1], color=color, lw=2.2, ls="--")

        _pin(ax,  0, 0, s=0.10)
        _roller(ax, 2, 0, s=0.10)

        ax.set_xlim(-0.3, 2.5)
        ax.set_ylim(-0.42, 1.55)
        ax.set_title(title, fontsize=11, fontweight="bold", color=color, pad=5)
        ax.text(1, -0.36, note, ha="center", fontsize=8.5, color=color)

    plt.tight_layout(pad=1.4)
    return fig


# ── 6. Solver truss (dynamic state) ──────────────────────────────────────────

def diagram_solver_state(highlight_joint=None, known_forces=None,
                         known_reactions=None):
    """
    Draws the 5-member solver truss.
    known_forces   : dict {member_name: float}  (positive = tension)
    known_reactions: dict {key: float}  (Ax, Ay, By)
    highlight_joint: str  e.g. 'A'
    """
    from solver import JOINTS, MEMBERS, MEMBER_NAMES

    known_forces    = known_forces    or {}
    known_reactions = known_reactions or {}

    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor(C_BG)
    _ax_clean(ax)

    # ── Members ───────────────────────────────────────────────────────────────
    for (a, b), name in zip(MEMBERS, MEMBER_NAMES):
        p1, p2 = JOINTS[a], JOINTS[b]
        if name in known_forces:
            f = known_forces[name]
            if abs(f) < 0.05:
                col, lw = C_ZERO, 2.5
            elif f > 0:
                col, lw = C_TEN, 2.8
            else:
                col, lw = C_CMP, 2.8
        else:
            col, lw = C_UNK, 2.0

        _member(ax, p1, p2, color=col, lw=lw)

        # Force label at midpoint
        if name in known_forces:
            mx, my = (p1 + p2) / 2
            f = known_forces[name]
            if abs(f) < 0.05:
                lbl, lc = "0", C_ZERO
            elif f > 0:
                lbl, lc = f"+{f:.1f} kN", C_TEN
            else:
                lbl, lc = f"{f:.1f} kN", C_CMP
            perp = np.array([-(p2[1]-p1[1]), p2[0]-p1[0]])
            perp = perp / np.linalg.norm(perp) * 0.22
            _force_label(ax, mx + perp[0], my + perp[1], lbl, lc)

    # ── Support reactions ─────────────────────────────────────────────────────
    if "Ay" in known_reactions:
        _arrow(ax, 0, 0, 0, 0.60, color=C_RXN,
               label=f"Ay={known_reactions['Ay']:.0f}", lpad=(0.28, 0))
    if "Ax" in known_reactions:
        _arrow(ax, 0, 0, 0.60, 0, color=C_RXN,
               label=f"Ax={known_reactions['Ax']:.0f}", lpad=(0, 0.18))
    if "By" in known_reactions:
        _arrow(ax, 4, 0, 0, 0.60, color=C_RXN,
               label=f"By={known_reactions['By']:.0f}", lpad=(0.28, 0))

    # ── Joints ────────────────────────────────────────────────────────────────
    for name, pos in JOINTS.items():
        off = (0, -0.38) if pos[1] == 0 else (0, 0.18)
        hl  = (name == highlight_joint)
        if hl:
            ax.add_patch(mpatches.Circle(pos, 0.28, color="#fde68a",
                                          zorder=4, lw=0))
        _joint(ax, *pos, label=name, off=off,
               fc="#f59e0b" if hl else C_JNT)

    # ── Supports ──────────────────────────────────────────────────────────────
    _pin(ax,    *JOINTS["A"])
    _roller(ax, *JOINTS["B"])

    # ── Applied load ──────────────────────────────────────────────────────────
    _arrow(ax, 2, 2, 0, -0.75, label="40 kN")

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=C_TEN,  label="Tension"),
        mpatches.Patch(color=C_CMP,  label="Compression"),
        mpatches.Patch(color=C_ZERO, label="Zero-force"),
        mpatches.Patch(color=C_UNK,  label="Unknown"),
    ]
    ax.legend(handles=legend_items, loc="upper right", fontsize=8,
              framealpha=0.9, edgecolor="#e2e8f0")

    ax.set_xlim(-1.0, 5.2)
    ax.set_ylim(-1.1, 3.3)
    ax.set_title("Truss Problem — Method of Joints",
                 fontsize=12, fontweight="bold", color="#0f172a", pad=8)
    plt.tight_layout()
    return fig


# ── 7. DSM node/DOF diagram ───────────────────────────────────────────────────

def diagram_dsm_nodes():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(C_BG)
    _ax_clean(ax)

    nodes = {1: (0.0, 0.0), 2: (4.0, 0.0), 3: (2.0, 2.0)}

    _member(ax, nodes[1], nodes[3], color=C_MBR)
    _member(ax, nodes[2], nodes[3], color=C_MBR)

    for n, (x, y) in nodes.items():
        _joint(ax, x, y, r=0.10)
        ax.text(x, y, str(n), ha="center", va="center",
                fontsize=11, fontweight="bold", color="white", zorder=9)

    # DOF labels
    dof_offs = {
        1: [(-0.55, -0.15, "u₁ (→)"),
            (-0.55,  0.15, "v₁ (↑)")],
        2: [( 0.20, -0.15, "u₂ (→)"),
            ( 0.20,  0.15, "v₂ (↑)")],
        3: [(-0.55, -0.10, "u₃ (→)"),
            (-0.55,  0.20, "v₃ (↑)")],
    }
    constrained = {1, 2, 3, 4}   # 1-indexed
    dof_counter = 1
    for n in sorted(nodes):
        x, y = nodes[n]
        for ox, oy, lbl in dof_offs[n]:
            is_con = dof_counter in constrained
            col = "#dc2626" if is_con else "#16a34a"
            ax.text(x + ox, y + oy, f"DOF {dof_counter}: {lbl}",
                    fontsize=8, color=col, ha="left" if ox > 0 else "right",
                    fontweight="bold")
            dof_counter += 1

    _pin(ax,    *nodes[1], s=0.14)
    _roller(ax, *nodes[2], s=0.14)

    # Load arrow
    _arrow(ax, 2, 2, 0, -0.75, label="P ↓")

    # Member labels
    m13 = (np.array(nodes[1]) + np.array(nodes[3])) / 2
    m23 = (np.array(nodes[2]) + np.array(nodes[3])) / 2
    ax.text(m13[0] - 0.35, m13[1], "Member 1\n(nodes 1–3)", ha="right",
            fontsize=8, color="#334155", style="italic")
    ax.text(m23[0] + 0.35, m23[1], "Member 2\n(nodes 2–3)", ha="left",
            fontsize=8, color="#334155", style="italic")

    # Legend
    ax.text(3.5, 2.5, "DOF colour\n● Red  = constrained\n● Green = free",
            fontsize=8, color="#0f172a",
            bbox=dict(boxstyle="round,pad=0.4", fc="#f8fafc", ec="#e2e8f0", lw=1))

    ax.set_xlim(-1.1, 5.1)
    ax.set_ylim(-1.2, 3.2)
    ax.set_title("DSM — Node Numbering & Degrees of Freedom",
                 fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    plt.tight_layout()
    return fig


def diagram_dsm_deformed(v3_mm: float, scale: float = 80.0):
    """Show original + deformed shape (scale exaggerated for visibility)."""
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor(C_BG)
    _ax_clean(ax)

    nodes = {1: np.array([0.0, 0.0]),
             2: np.array([4.0, 0.0]),
             3: np.array([2.0, 2.0])}

    # Original (grey)
    for (i, j) in [(1, 3), (2, 3)]:
        _member(ax, nodes[i], nodes[j], color="#cbd5e1", lw=2.0)

    # Deformed (blue) — v3 is downward so add scaled displacement
    def3 = nodes[3] + np.array([0.0, v3_mm / 1000.0 * scale])
    _member(ax, nodes[1], def3, color=C_JNT, lw=2.5)
    _member(ax, nodes[2], def3, color=C_JNT, lw=2.5)

    # Joints
    for n, p in nodes.items():
        _joint(ax, *p, r=0.09, fc="#94a3b8")
    _joint(ax, *def3, r=0.09, fc=C_JNT)
    ax.annotate(f"Node 3 displaced\n{v3_mm:.2f} mm ↓",
                xy=def3, xytext=(def3[0] + 0.6, def3[1] - 0.3),
                fontsize=9, color=C_JNT,
                arrowprops=dict(arrowstyle="->", color=C_JNT, lw=1.2))

    _pin(ax,    *nodes[1], s=0.14)
    _roller(ax, *nodes[2], s=0.14)

    ax.text(2, 2.6,
            f"Scale factor: ×{scale:.0f}\n"
            f"Actual δ = {abs(v3_mm):.3f} mm",
            ha="center", fontsize=9, color="#334155",
            bbox=dict(boxstyle="round,pad=0.4", fc="#f8fafc", ec="#e2e8f0"))

    ax.set_xlim(-0.8, 5.0)
    ax.set_ylim(-0.9, 3.1)
    ax.set_title("Deformed Shape (exaggerated scale)",
                 fontsize=12, fontweight="bold", color="#0f172a", pad=8)
    plt.tight_layout()
    return fig
