"""Professional truss diagrams rendered with matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

C_MBR   = '#1e3a5f'
C_TEN   = '#16a34a'
C_CMP   = '#dc2626'
C_JNT   = '#2563eb'
C_SUP   = '#4b5563'
C_LOAD  = '#b45309'
C_RXNP  = '#7c3aed'
C_CUT   = '#ef4444'
C_BG    = '#f8fafc'


def _ax(ax):
    ax.set_facecolor(C_BG)
    ax.set_aspect('equal')
    ax.axis('off')


def _mbr(ax, p1, p2, color=C_MBR, lw=2.8, zorder=2, ls='-'):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], ls,
            color=color, lw=lw, solid_capstyle='round',
            dash_capstyle='round', zorder=zorder)


def _jnt(ax, x, y, label=None, off=(0, 0.18), fs=11):
    ax.plot(x, y, 'o', color='white',  markersize=15, zorder=5)
    ax.plot(x, y, 'o', color=C_JNT,   markersize=11, zorder=6)
    ax.plot(x, y, 'o', color='white',  markersize=5,  zorder=7)
    if label:
        ax.text(x + off[0], y + off[1], label, ha='center', va='bottom',
                fontsize=fs, fontweight='bold', color='#0f172a', zorder=8)


def _pin(ax, x, y, s=0.18):
    ax.add_patch(plt.Polygon([(x, y), (x - s, y - s * 1.4), (x + s, y - s * 1.4)],
                             color=C_SUP, zorder=1))
    ax.plot([x - s * 1.4, x + s * 1.4], [y - s * 1.4, y - s * 1.4],
            color=C_SUP, lw=1.8, zorder=1)
    for i in range(5):
        xi = x - s * 1.2 + i * s * 0.6
        ax.plot([xi, xi - s * 0.22], [y - s * 1.4, y - s * 1.7],
                color=C_SUP, lw=1, zorder=1)


def _roller(ax, x, y, s=0.18):
    ax.add_patch(plt.Polygon([(x, y), (x - s, y - s * 1.1), (x + s, y - s * 1.1)],
                             color=C_SUP, zorder=1))
    ax.add_patch(plt.Circle((x, y - s * 1.45), s * 0.27,
                            color=C_SUP, fill=False, lw=1.8, zorder=1))
    ax.plot([x - s * 1.4, x + s * 1.4], [y - s * 1.75, y - s * 1.75],
            color=C_SUP, lw=1.8, zorder=1)


def _arrow(ax, x, y, dx, dy, color=C_LOAD, label='', loff=(0.14, 0)):
    ax.annotate('', xy=(x + dx, y + dy), xytext=(x, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=2,
                                mutation_scale=16))
    if label:
        ax.text(x + dx / 2 + loff[0], y + dy / 2 + loff[1],
                label, color=color, fontsize=10, fontweight='bold',
                ha='center', va='center', zorder=9)


# ── 1. What is a Truss ───────────────────────────────────────────────────────

def diagram_basic_truss():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(C_BG)
    _ax(ax)

    J = {'A': np.array([0.0, 0.0]),
         'B': np.array([4.0, 0.0]),
         'C': np.array([2.0, 2.3])}

    for p, q in [('A', 'B'), ('A', 'C'), ('B', 'C')]:
        _mbr(ax, J[p], J[q])

    # Member labels
    for (p, q), txt, ha, off in [
        (('A', 'B'), 'Bottom Chord', 'center', (0, -0.25)),
        (('A', 'C'), 'Left Rafter', 'right',  (-0.15, 0)),
        (('B', 'C'), 'Right Rafter', 'left',   (0.15, 0)),
    ]:
        mid = (J[p] + J[q]) / 2
        ax.text(mid[0] + off[0], mid[1] + off[1], txt, ha=ha,
                fontsize=8.5, color='#334155', style='italic')

    _jnt(ax, *J['A'], label='A', off=(0, -0.38))
    _jnt(ax, *J['B'], label='B', off=(0, -0.38))
    _jnt(ax, *J['C'], label='C')

    _pin(ax, *J['A'])
    _roller(ax, *J['B'])

    ax.text(0,  -0.75, 'Pin support\n(Ax, Ay)', ha='center', fontsize=8, color='#64748b')
    ax.text(4,  -0.75, 'Roller support\n(By)', ha='center', fontsize=8, color='#64748b')

    _arrow(ax, 2, 2.3, 0, -0.75, label='P', loff=(0.14, 0))
    _arrow(ax, 0, 0,  0,  0.6,  color=C_RXNP, label='Ay', loff=(0.18, 0))
    _arrow(ax, 0, 0,  0.6, 0,   color=C_RXNP, label='Ax', loff=(0, 0.14))
    _arrow(ax, 4, 0,  0,  0.6,  color=C_RXNP, label='By', loff=(0.18, 0))

    # Annotation: joints
    ax.text(4.6, 1.1, '3 Joints\n3 Members\n3 Reactions\n→ Determinate',
            fontsize=8.5, color='#0f172a', va='center',
            bbox=dict(boxstyle='round,pad=0.5', fc='#e0f2fe', ec='#0284c7', lw=1.2))

    ax.set_xlim(-1.0, 5.5)
    ax.set_ylim(-1.2, 3.3)
    ax.set_title('Simple Triangular Truss — Joints, Members & Supports',
                 fontsize=12, fontweight='bold', color='#0f172a', pad=10)
    plt.tight_layout()
    return fig


# ── 2. Truss Types ───────────────────────────────────────────────────────────

def _parallel_truss(ax, diagonals, title, tag_t='T', tag_c='C'):
    """Draw a 3-panel parallel-chord truss given a list of diagonal (i,j) tuples.
       Bottom nodes 0-3, top nodes 4-7."""
    B = [(i, 0) for i in range(4)]
    T = [(i, 1) for i in range(4)]

    # Bottom & top chords
    for i in range(3):
        _mbr(ax, B[i], B[i + 1])
        _mbr(ax, T[i], T[i + 1])

    # Verticals (for Pratt and Howe only — caller decides)
    for d in diagonals:
        src, dst = d
        if src < 4:
            p1, p2 = B[src], T[dst - 4]
        else:
            p1, p2 = T[src - 4], B[dst]
        # Color diagonals differently
        _mbr(ax, p1, p2, color=C_TEN, lw=2.2)

    _ax(ax)
    ax.set_xlim(-0.4, 3.4)
    ax.set_ylim(-0.5, 1.5)
    ax.set_title(title, fontsize=10, fontweight='bold', color='#0f172a', pad=6)


def diagram_truss_types():
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    fig.patch.set_facecolor(C_BG)

    configs = [
        ('Pratt Truss',  True,  [(0, 5), (1, 6), (2, 7)]),   # diag /
        ('Warren Truss', False, [(0, 5), (5, 2), (2, 7)]),   # alternating
        ('Howe Truss',   True,  [(4, 1), (5, 2), (6, 3)]),   # diag \
    ]
    labels = [
        'Diagonals in tension\nunder gravity load',
        'No vertical members\nAlternating diagonals',
        'Diagonals in compression\nunder gravity load',
    ]

    for ax, (title, has_vert, diags), lbl in zip(axes, configs, labels):
        B = [(i, 0) for i in range(4)]
        T = [(i, 1) for i in range(4)]
        _ax(ax)

        # Chords
        for i in range(3):
            _mbr(ax, B[i], B[i + 1])
            _mbr(ax, T[i], T[i + 1])

        # Verticals
        if has_vert:
            for i in range(4):
                _mbr(ax, B[i], T[i], color='#475569', lw=2.2)

        # Diagonals
        for src, dst in diags:
            if src < 4:
                p1, p2 = B[src], T[dst - 4]
            else:
                p1, p2 = T[src - 4], B[dst]
            _mbr(ax, p1, p2, color=C_TEN, lw=2.2)

        # Joints
        for x, y in B + T:
            _jnt(ax, x, y)

        _pin(ax, 0, 0, s=0.12)
        _roller(ax, 3, 0, s=0.12)

        ax.set_xlim(-0.5, 3.7)
        ax.set_ylim(-0.55, 1.55)
        ax.set_title(title, fontsize=11, fontweight='bold', color='#0f172a', pad=6)
        ax.text(1.5, -0.42, lbl, ha='center', fontsize=7.5, color='#475569',
                style='italic')

    plt.tight_layout(pad=1.0)
    return fig


# ── 3. Method of Joints ──────────────────────────────────────────────────────

def diagram_method_joints():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    fig.patch.set_facecolor(C_BG)

    # Left: full 3-panel truss with joint B highlighted
    B = [(i, 0) for i in range(4)]
    T = [(i, 1) for i in range(4)]
    _ax(ax1)
    for i in range(3):
        _mbr(ax1, B[i], B[i + 1])
        _mbr(ax1, T[i], T[i + 1])
    for i in range(4):
        _mbr(ax1, B[i], T[i], color='#475569', lw=2)
    for src, dst in [(0, 5), (1, 6), (2, 7)]:
        _mbr(ax1, B[src], T[dst - 4], color=C_TEN, lw=2)

    for i, (x, y) in enumerate(B):
        _jnt(ax1, x, y, label=str(i + 1), off=(0, -0.28), fs=9)
    for i, (x, y) in enumerate(T):
        _jnt(ax1, x, y, label=chr(65 + i), fs=9)

    _pin(ax1, 0, 0, s=0.14)
    _roller(ax1, 3, 0, s=0.14)
    _arrow(ax1, 1, 1, 0, -0.5, label='P', loff=(0.14, 0))
    _arrow(ax1, 2, 1, 0, -0.5, label='P', loff=(0.14, 0))

    # Highlight joint A (top-left)
    circle = plt.Circle((0, 1), 0.25, color='#fbbf24', fill=False, lw=2.5, ls='--', zorder=8)
    ax1.add_patch(circle)
    ax1.text(0, 1.4, 'Analyse\nthis joint', ha='center', fontsize=8.5,
             color='#b45309', fontweight='bold')

    ax1.set_xlim(-0.6, 4.2)
    ax1.set_ylim(-0.7, 1.9)
    ax1.set_title('Step 1 — Start at a joint with ≤2 unknowns', fontsize=11,
                  fontweight='bold', color='#0f172a', pad=8)

    # Right: FBD of joint A
    _ax(ax2)
    ox, oy = 1.5, 1.5  # origin of FBD
    ax2.plot(ox, oy, 'o', color='#fbbf24', markersize=20, zorder=5)
    ax2.plot(ox, oy, 'o', color=C_JNT,    markersize=14, zorder=6)
    ax2.plot(ox, oy, 'o', color='white',   markersize=6,  zorder=7)
    ax2.text(ox, oy + 0.08, 'A', ha='center', va='center', fontsize=11,
             fontweight='bold', color='white', zorder=8)

    # Member forces from A
    _arrow(ax2, ox, oy, 0.9, 0,   color=C_TEN,  label='F_AB (tension → )',     loff=(0, 0.18))
    _arrow(ax2, ox, oy, 0.7, -0.7, color=C_CMP, label='F_A1 (compression ↘)', loff=(0.55, 0.08))
    _arrow(ax2, ox, oy, 0, 0.8,   color=C_RXNP, label='Ay (reaction ↑)',       loff=(0.55, 0))
    _arrow(ax2, ox, oy, 0.8, 0,   color=C_RXNP, label='Ax (reaction →)',       loff=(0, -0.18))

    ax2.text(ox, oy - 0.55, 'ΣFx = 0:  Ax + F_AB cos θ = 0\nΣFy = 0:  Ay + F_A1 sin θ = 0',
             ha='center', fontsize=9, color='#0f172a',
             bbox=dict(boxstyle='round,pad=0.5', fc='#dbeafe', ec='#3b82f6', lw=1.2))

    ax2.set_xlim(0.0, 3.5)
    ax2.set_ylim(0.2, 3.0)
    ax2.set_title('Step 2 — Free-Body Diagram at Joint A', fontsize=11,
                  fontweight='bold', color='#0f172a', pad=8)

    plt.tight_layout(pad=1.0)
    return fig


# ── 4. Method of Sections ────────────────────────────────────────────────────

def diagram_method_sections():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor(C_BG)
    _ax(ax)

    B = [(i, 0) for i in range(5)]
    T = [(i, 1) for i in range(5)]

    for i in range(4):
        col = '#cbd5e1' if i == 1 else C_MBR
        _mbr(ax, B[i], B[i + 1], color=col)
        _mbr(ax, T[i], T[i + 1], color=col)
    for i in range(5):
        col = '#cbd5e1' if i == 1 else '#475569'
        _mbr(ax, B[i], T[i], color=col, lw=2)
    for src, dst in [(0, 5), (1, 6), (2, 7), (3, 8)]:
        col = '#cbd5e1' if src in (1, 2) else C_TEN
        _mbr(ax, B[src], T[dst - 4], color=col, lw=2)

    # Highlight the 3 cut members
    _mbr(ax, T[1], T[2], color=C_CUT, lw=3.5)     # top chord cut
    _mbr(ax, B[1], T[2], color=C_CUT, lw=3.5)     # diagonal cut
    _mbr(ax, B[1], B[2], color=C_CUT, lw=3.5)     # bottom chord cut

    for x, y in B:
        _jnt(ax, x, y)
    for x, y in T:
        _jnt(ax, x, y)

    _pin(ax, 0, 0, s=0.13)
    _roller(ax, 4, 0, s=0.13)
    _arrow(ax, 2, 1, 0, -0.5, label='P')
    _arrow(ax, 0, 0, 0, 0.55, color=C_RXNP, label='Ay')
    _arrow(ax, 4, 0, 0, 0.55, color=C_RXNP, label='By')

    # Cut plane
    ax.plot([1.55, 1.55], [-0.4, 1.55], color=C_CUT, lw=2.5, ls='--', zorder=9)
    ax.text(1.55, -0.52, 'Cut', ha='center', fontsize=9, color=C_CUT, fontweight='bold')

    # Labels for cut forces
    ax.text(1.4, 1.12, 'F₁ (top)', fontsize=9, color=C_CUT, ha='right', fontweight='bold')
    ax.text(1.1, 0.55, 'F₂ (diag)', fontsize=9, color=C_CUT, ha='right', fontweight='bold')
    ax.text(1.4, -0.15, 'F₃ (bot)', fontsize=9, color=C_CUT, ha='right', fontweight='bold')

    # Equations box
    ax.text(3.5, 0.5, 'ΣFx = 0\nΣFy = 0\nΣM = 0\n→ solve F₁, F₂, F₃',
            fontsize=9, color='#0f172a', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.5', fc='#fef9c3', ec='#ca8a04', lw=1.2))

    ax.set_xlim(-0.6, 5.2)
    ax.set_ylim(-0.8, 1.9)
    ax.set_title('Method of Sections — Cut Plane Through ≤3 Members',
                 fontsize=12, fontweight='bold', color='#0f172a', pad=10)
    plt.tight_layout()
    return fig


# ── 5. Determinacy ───────────────────────────────────────────────────────────

def _small_truss(ax, extra_members, label, color, note):
    B = [(0, 0), (1, 0), (2, 0)]
    T = [(0.5, 1), (1.5, 1)]
    members = [
        (B[0], B[1]), (B[1], B[2]),
        (B[0], T[0]), (B[1], T[0]), (B[1], T[1]),
        (B[2], T[1]), (T[0], T[1]),
    ]
    for p, q in members:
        _mbr(ax, p, q, color='#1e3a5f', lw=2.2)
    for p, q in extra_members:
        _mbr(ax, p, q, color=color, lw=2.2, ls='--')

    for x, y in B:
        _jnt(ax, x, y)
    for x, y in T:
        _jnt(ax, x, y)

    _pin(ax, 0, 0, s=0.1)
    _roller(ax, 2, 0, s=0.1)
    _ax(ax)
    ax.set_xlim(-0.3, 2.6)
    ax.set_ylim(-0.45, 1.55)
    ax.set_title(label, fontsize=10.5, fontweight='bold', color=color, pad=5)
    ax.text(1, -0.38, note, ha='center', fontsize=8.5, color=color)


def diagram_determinacy():
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    fig.patch.set_facecolor(C_BG)

    B = [(0, 0), (1, 0), (2, 0)]
    T = [(0.5, 1), (1.5, 1)]

    # Determinate: m=7, r=3, j=5 → 7+3=10=2×5 ✓
    _small_truss(axes[0], [], 'Statically Determinate', '#16a34a',
                 'm + r = 2j  →  7 + 3 = 2×5  ✓')

    # Indeterminate: add one extra member
    _small_truss(axes[1], [(B[0], T[1])], 'Statically Indeterminate', '#d97706',
                 'm + r > 2j  →  8 + 3 > 10')

    # Unstable: remove one member
    _small_truss(axes[2], [], 'Unstable (Mechanism)', '#dc2626',
                 'm + r < 2j  →  6 + 3 < 10')
    # Remove a member visually by overdrawing in background color
    axes[2].plot([B[1][0], T[1][0]], [B[1][1], T[1][1]],
                 color=C_BG, lw=4, zorder=3)  # erase one member

    plt.tight_layout(pad=1.2)
    return fig
