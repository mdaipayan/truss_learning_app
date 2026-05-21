"""Truss Learning App — gamified Streamlit web app."""

import random
import re
import matplotlib.pyplot as plt
import streamlit as st

import game
import diagrams
from questions import TUTORIALS, QUESTIONS

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Truss Learning App", page_icon="🔺",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"]          { background: #1e293b; }
[data-testid="stSidebar"] .stMarkdown p { color: #94a3b8; }

/* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    color: #cbd5e1;
    border: 1px solid #334155;
    border-radius: 8px;
    width: 100%;
    text-align: left;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #334155;
    color: #f1f5f9;
    border-color: #475569;
}

/* ── Level badge ── */
.lvl-badge {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    font-weight: 700;
    font-size: 0.9em;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 4px;
}

/* ── XP bar container ── */
.xp-label { color: #94a3b8; font-size: 0.82em; margin-bottom: 2px; }

/* ── Achievement cards ── */
.ach-card {
    background: #1e293b;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    border: 1px solid #334155;
    transition: border-color 0.2s;
}
.ach-card.unlocked { border-color: #2563eb; }
.ach-card.locked   { opacity: 0.45; filter: grayscale(80%); }

/* ── Quiz answer buttons ── */
div[data-testid="stVerticalBlock"] .stButton > button.ans-btn {
    background: #1e293b;
    color: #e2e8f0;
    border: 1.5px solid #334155;
    border-radius: 10px;
    text-align: left;
    width: 100%;
    padding: 12px 18px;
    font-size: 1em;
    margin-bottom: 4px;
    transition: all 0.15s;
}
div[data-testid="stVerticalBlock"] .stButton > button.ans-btn:hover {
    border-color: #2563eb;
    background: #1d3461;
}

/* ── Streak pill ── */
.streak-pill {
    display: inline-block;
    background: linear-gradient(90deg, #f97316, #ef4444);
    color: white;
    font-weight: 800;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 1em;
}

/* ── Section headers ── */
h1, h2, h3 { color: #f1f5f9 !important; }
p, li       { color: #cbd5e1; }

/* ── Info/success/warning/error overrides ── */
[data-testid="stAlert"] { border-radius: 10px; }

/* ── Metric ── */
[data-testid="stMetric"] label { color: #94a3b8 !important; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #f1f5f9 !important; }

/* ── Diagram containers ── */
[data-testid="stImage"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session-state init ────────────────────────────────────────────────────────

def _init():
    if "gs" not in st.session_state:
        st.session_state.gs = game.load()
    defaults = {
        "page":          "home",
        "tut_idx":       0,
        "quiz_pool":     None,
        "quiz_idx":      0,
        "quiz_score":    0,
        "quiz_wrong":    [],
        "quiz_answered": False,
        "quiz_selected": None,
        "quiz_topic":    None,
        "streak":        0,
        "toasts":        [],    # pending achievement toasts
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


def _strip_rich(text: str) -> str:
    return re.sub(r'\[/?[^\]]+\]', '', text)


# ── Diagram map (one per tutorial index) ─────────────────────────────────────

DIAGRAM_FNS = [
    diagrams.diagram_basic_truss,
    diagrams.diagram_truss_types,
    diagrams.diagram_method_joints,
    diagrams.diagram_method_sections,
    diagrams.diagram_determinacy,
]

# ── Sidebar ───────────────────────────────────────────────────────────────────

def _sidebar():
    g = gs()
    lv = game.get_level(g["xp"])
    xp_done, xp_band = game.xp_to_next_level(g["xp"])
    n_ach = len(g["unlocked"])

    with st.sidebar:
        st.markdown("## 🔺 Truss Learning")
        st.divider()

        # Player card
        st.markdown(f'<div class="lvl-badge">{lv["icon"]} {lv["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="xp-label">{g["xp"]} XP{" · " + str(xp_done) + "/" + str(xp_band) + " to next level" if xp_band else " · MAX LEVEL"}</div>', unsafe_allow_html=True)
        if xp_band:
            st.progress(xp_done / xp_band)
        st.caption(f"🏅 {n_ach}/{len(game.ACHIEVEMENTS)} achievements")
        st.divider()

        # Nav
        nav_items = [
            ("🏠", "Home",        "home"),
            ("📖", "Learn",       "tutorials"),
            ("⚔️", "Challenge",   "quiz_menu"),
            ("🏅", "Achievements","achievements"),
            ("📋", "Reference",   "reference"),
        ]
        for icon, label, pg in nav_items:
            if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{pg}"):
                go(pg)

        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("Correct", g["total_correct"])
        col2.metric("Answered", g["total_answered"])
        acc = (g["total_correct"] / g["total_answered"] * 100) if g["total_answered"] else 0
        st.caption(f"Accuracy: {acc:.0f}%  •  Best streak: {g['best_streak']} 🔥")


_sidebar()

# ── Achievement toasts ────────────────────────────────────────────────────────

for toast in st.session_state.toasts:
    st.toast(f"{toast['icon']} **{toast['name']}** unlocked! +{toast['xp']} XP", icon="🎉")
st.session_state.toasts = []


# ════════════════════════════════════════════════════════════════════════════════
# PAGES
# ════════════════════════════════════════════════════════════════════════════════

# ── Home ──────────────────────────────────────────────────────────────────────

def page_home():
    g = gs()
    lv = game.get_level(g["xp"])

    st.title(f"🔺 Truss Learning App")
    st.subheader("Master structural analysis — one concept at a time")
    st.write("")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Level", f'{lv["icon"]} {lv["name"]}')
    col2.metric("Total XP", g["xp"])
    col3.metric("Tutorials Read", f'{len(g["tutorials_read"])}/5')
    col4.metric("Accuracy", f'{(g["total_correct"]/g["total_answered"]*100):.0f}%' if g["total_answered"] else "—")

    st.write("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 📖 Learn")
        st.markdown("5 illustrated tutorials covering truss basics, types, and analysis methods. Earn **+15 XP** per topic.")
        if st.button("Start Learning →", key="h_learn", use_container_width=True, type="primary"):
            go("tutorials")
    with c2:
        st.markdown("#### ⚔️ Challenge")
        st.markdown("13 quiz questions with instant feedback, streaks, and XP bonuses. Earn **+20 XP** per correct answer.")
        if st.button("Take a Quiz →", key="h_quiz", use_container_width=True, type="primary"):
            go("quiz_menu")
    with c3:
        st.markdown("#### 🏅 Achievements")
        st.markdown(f"You've unlocked **{len(g['unlocked'])}/{len(game.ACHIEVEMENTS)}** badges. Unlock them all for bonus XP!")
        if st.button("View Achievements →", key="h_ach", use_container_width=True):
            go("achievements")

    st.divider()
    st.markdown("#### 🗺️ XP Roadmap")
    cols = st.columns(len(game.LEVELS))
    for col, lv_info in zip(cols, game.LEVELS):
        unlocked = g["xp"] >= lv_info["min_xp"]
        style = "✅" if unlocked else "🔒"
        col.markdown(f"**{lv_info['icon']} {lv_info['name']}**")
        col.caption(f"{style} {lv_info['min_xp']} XP")


# ── Tutorials ─────────────────────────────────────────────────────────────────

def page_tutorials():
    g = gs()

    st.title("📖 Learn — Illustrated Tutorials")
    st.write("")

    topics = [t["title"] for t in TUTORIALS]
    sel = st.radio("Select a topic:", topics, index=st.session_state.tut_idx,
                   horizontal=True)
    idx = topics.index(sel)
    st.session_state.tut_idx = idx

    st.divider()

    tut = TUTORIALS[idx]
    read_before = idx in g["tutorials_read"]

    col_title, col_badge = st.columns([4, 1])
    with col_title:
        st.subheader(f"{idx + 1}. {tut['title']}")
        st.caption(f"Topic {idx + 1} of {len(TUTORIALS)}")
    with col_badge:
        if read_before:
            st.success("✅ Completed", icon="🏆")
        else:
            st.info("+15 XP on read", icon="⭐")

    # Diagram
    fig = DIAGRAM_FNS[idx]()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.write("")

    # Tutorial content (strip Rich markup, render as markdown)
    content = _strip_rich(tut["content"])
    # Make bullet points and formulas look nicer
    st.markdown(content)

    st.write("")

    col_prev, col_mark, col_next = st.columns([1, 2, 1])
    with col_prev:
        if idx > 0 and st.button("← Previous", use_container_width=True):
            st.session_state.tut_idx = idx - 1
            st.rerun()
    with col_mark:
        btn_label = "✅ Already read" if read_before else "📖 Mark as read (+15 XP)"
        if st.button(btn_label, use_container_width=True,
                     type="secondary" if read_before else "primary",
                     disabled=read_before):
            if idx not in g["tutorials_read"]:
                g["tutorials_read"].append(idx)
                old_lvl = game.get_level_index(g["xp"])
                g["xp"] += 15
                new_ach = game.check_achievements(g, st.session_state.streak,
                                                  None, None)
                st.session_state.toasts.extend(new_ach)
                if game.get_level_index(g["xp"]) > old_lvl:
                    st.balloons()
                _save()
                st.rerun()
    with col_next:
        if idx < len(TUTORIALS) - 1 and st.button("Next →", use_container_width=True):
            st.session_state.tut_idx = idx + 1
            st.rerun()


# ── Quiz menu ─────────────────────────────────────────────────────────────────

def page_quiz_menu():
    st.title("⚔️ Challenge — Quiz Mode")
    st.markdown("Answer questions, earn XP, and build your streak!")
    st.write("")

    topics = sorted({q["topic"] for q in QUESTIONS})
    col1, col2 = st.columns([1, 2])
    with col1:
        mode = st.radio("Quiz mode:", ["All topics"] + topics, key="qmode")
    with col2:
        if mode == "All topics":
            pool_size = len(QUESTIONS)
            st.metric("Questions", pool_size)
            st.caption("Covers: " + " · ".join(topics))
        else:
            pool_size = sum(1 for q in QUESTIONS if q["topic"] == mode)
            st.metric("Questions", pool_size)
            st.caption(f"Topic: {mode}")

        st.write("")
        st.markdown("**XP breakdown:**")
        st.markdown("- ✅ Correct answer: **+20 XP**")
        st.markdown("- 🔥 Streak ×3: **+10 bonus XP**")
        st.markdown("- ⚡ Streak ×5: **+20 bonus XP**")
        st.markdown("- 🏅 Perfect score: **+50 bonus XP**")

    st.write("")
    if st.button("▶  Start Quiz", type="primary"):
        pool = QUESTIONS[:] if mode == "All topics" else [q for q in QUESTIONS if q["topic"] == mode]
        random.shuffle(pool)
        st.session_state.quiz_pool     = pool
        st.session_state.quiz_idx      = 0
        st.session_state.quiz_score    = 0
        st.session_state.quiz_wrong    = []
        st.session_state.quiz_answered = False
        st.session_state.quiz_selected = None
        st.session_state.quiz_topic    = mode
        st.session_state.streak        = 0
        go("quiz_question")


# ── Quiz question ─────────────────────────────────────────────────────────────

def page_quiz_question():
    pool     = st.session_state.quiz_pool
    idx      = st.session_state.quiz_idx
    streak   = st.session_state.streak
    answered = st.session_state.quiz_answered
    selected = st.session_state.quiz_selected

    if pool is None or idx >= len(pool):
        go("quiz_results")

    q = pool[idx]

    # Header row
    hcol1, hcol2, hcol3 = st.columns([3, 1, 1])
    with hcol1:
        st.progress((idx) / len(pool),
                    text=f"Question {idx + 1} / {len(pool)}")
    with hcol2:
        st.metric("Score", f"{st.session_state.quiz_score}/{idx}")
    with hcol3:
        if streak >= 5:
            st.markdown(f'<div class="streak-pill">⚡ {streak} streak!</div>', unsafe_allow_html=True)
        elif streak >= 3:
            st.markdown(f'<div class="streak-pill">🔥 {streak} streak!</div>', unsafe_allow_html=True)
        elif streak > 0:
            st.markdown(f"🔥 ×{streak}")

    st.write("")
    st.markdown(f"### Q{idx + 1}. {q['question']}")
    st.caption(f"Topic: **{q['topic']}**")
    st.write("")

    # Answer options
    for i, opt in enumerate(q["options"]):
        if answered:
            if i == q["answer"]:
                st.success(f"✅  {opt}")
            elif i == selected:
                st.error(f"❌  {opt}")
            else:
                st.button(opt, key=f"opt_{i}", disabled=True)
        else:
            if st.button(opt, key=f"opt_{i}", use_container_width=True):
                _handle_answer(i, q)
                st.rerun()

    # Post-answer feedback
    if answered:
        st.write("")
        correct = selected == q["answer"]
        if correct:
            xp_gained = 20
            bonus = 0
            if streak >= 5:
                bonus = 20
            elif streak >= 3:
                bonus = 10
            if bonus:
                st.success(f"**Correct! +{xp_gained} XP** + 🔥 {bonus} streak bonus!")
            else:
                st.success(f"**Correct! +{xp_gained} XP**")
        else:
            st.error(f"**Incorrect.** The correct answer was: *{q['options'][q['answer']]}*")

        st.info(f"💡 **Explanation:** {q['explanation']}")
        st.write("")

        is_last = idx + 1 >= len(pool)
        btn = "🏁 See Results" if is_last else "Next Question →"
        if st.button(btn, type="primary"):
            st.session_state.quiz_idx      = idx + 1
            st.session_state.quiz_answered = False
            st.session_state.quiz_selected = None
            if is_last:
                _finish_quiz()
            st.rerun()


def _handle_answer(selected: int, q: dict):
    g = gs()
    correct = selected == q["answer"]
    st.session_state.quiz_selected = selected
    st.session_state.quiz_answered = True

    g["total_answered"] += 1
    if correct:
        st.session_state.quiz_score += 1
        st.session_state.streak     += 1
        g["total_correct"]          += 1
        # XP
        xp = 20
        if st.session_state.streak >= 5:
            xp += 20
        elif st.session_state.streak >= 3:
            xp += 10
        old_lvl = game.get_level_index(g["xp"])
        g["xp"] += xp
        if game.get_level_index(g["xp"]) > old_lvl:
            st.balloons()
    else:
        st.session_state.streak = 0
        st.session_state.quiz_wrong.append(q)

    if st.session_state.streak > g["best_streak"]:
        g["best_streak"] = st.session_state.streak

    _save()


def _finish_quiz():
    g = gs()
    pool  = st.session_state.quiz_pool
    score = st.session_state.quiz_score
    total = len(pool)

    # Perfect bonus
    if score == total:
        old_lvl = game.get_level_index(g["xp"])
        g["xp"] += 50
        if game.get_level_index(g["xp"]) > old_lvl:
            st.balloons()

    new_ach = game.check_achievements(
        g,
        st.session_state.streak,
        st.session_state.quiz_topic,
        total,
    )
    st.session_state.toasts.extend(new_ach)
    _save()


# ── Quiz results ──────────────────────────────────────────────────────────────

def page_quiz_results():
    g     = gs()
    pool  = st.session_state.quiz_pool or []
    score = st.session_state.quiz_score
    total = len(pool)
    wrong = st.session_state.quiz_wrong
    pct   = score / total * 100 if total else 0

    st.title("📊 Quiz Results")
    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score",      f"{score} / {total}")
    c2.metric("Percentage", f"{pct:.0f}%")
    c3.metric("Incorrect",  len(wrong))
    c4.metric("Best Streak", f"{g['best_streak']} 🔥")

    st.progress(score / total if total else 0)
    st.write("")

    if pct == 100:
        st.success("🎉 Perfect score! Outstanding work. +50 bonus XP awarded!")
        st.balloons()
    elif pct >= 75:
        st.success("👍 Great job! Review the topics you missed to reach 100%.")
    elif pct >= 50:
        st.warning("📚 Good effort. Work through the tutorials on the weaker topics.")
    else:
        st.error("🔁 More study needed. Head back to the tutorials and try again.")

    if wrong:
        st.write("")
        st.markdown("**Topics to review:**")
        seen = set()
        for q in wrong:
            if q["topic"] not in seen:
                st.markdown(f"- 📖 **{q['topic']}**")
                seen.add(q["topic"])

    st.write("")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🔁 Retry", use_container_width=True):
            pool2 = st.session_state.quiz_pool[:]
            random.shuffle(pool2)
            st.session_state.quiz_pool     = pool2
            st.session_state.quiz_idx      = 0
            st.session_state.quiz_score    = 0
            st.session_state.quiz_wrong    = []
            st.session_state.quiz_answered = False
            st.session_state.quiz_selected = None
            st.session_state.streak        = 0
            go("quiz_question")
    with col_b:
        if st.button("📝 New Quiz", use_container_width=True):
            go("quiz_menu")
    with col_c:
        if st.button("📖 Tutorials", use_container_width=True):
            go("tutorials")


# ── Achievements ──────────────────────────────────────────────────────────────

def page_achievements():
    g = gs()
    unlocked = set(g["unlocked"])

    st.title("🏅 Achievements")
    st.caption(f"{len(unlocked)} / {len(game.ACHIEVEMENTS)} unlocked")
    st.write("")

    cols = st.columns(2)
    for i, ach in enumerate(game.ACHIEVEMENTS):
        is_unlocked = ach["id"] in unlocked
        card_class  = "ach-card unlocked" if is_unlocked else "ach-card locked"
        status      = "✅ Unlocked" if is_unlocked else f"🔒 Locked — +{ach['xp']} XP on unlock"
        with cols[i % 2]:
            st.markdown(f"""
<div class="{card_class}">
  <span style="font-size:1.8em">{ach['icon']}</span>
  <strong style="color:{'#f1f5f9' if is_unlocked else '#94a3b8'}"> {ach['name']}</strong><br>
  <span style="color:#94a3b8; font-size:0.88em">{ach['desc']}</span><br>
  <span style="color:{'#22c55e' if is_unlocked else '#64748b'}; font-size:0.82em">{status}</span>
</div>""", unsafe_allow_html=True)


# ── Reference ─────────────────────────────────────────────────────────────────

def page_reference():
    st.title("📋 Quick Reference Card")
    st.caption("Key formulas and rules for planar truss analysis")
    st.write("")

    st.subheader("Determinacy Formula")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""
| Condition | Result |
|-----------|--------|
| m + r = 2j | ✅ Statically determinate |
| m + r < 2j | ❌ Unstable (mechanism) |
| m + r > 2j | ⚠️ Statically indeterminate |
""")
    with c2:
        st.info("**Variables**\n\n- **m** — number of members\n- **r** — number of reaction components\n- **j** — number of joints")

    st.subheader("Method of Joints")
    st.markdown("""
| Rule | Detail |
|------|--------|
| Equilibrium equations | ΣFx = 0 and ΣFy = 0 per joint |
| Where to start | Joint with **≤ 2 unknown members** |
| Sign convention | Assume tension → negative result means compression |
| Zero-force rule A | 2 members, non-collinear, no load → both zero-force |
| Zero-force rule B | 3 members, 2 collinear, no load → third is zero-force |
""")

    st.subheader("Method of Sections")
    st.markdown("""
| Rule | Detail |
|------|--------|
| Equilibrium equations | ΣFx = 0, ΣFy = 0, ΣM = 0 for cut section |
| Maximum unknowns | **Cut ≤ 3 members** |
| Best moment point | Intersection of the **other two** unknown forces |
| Best use case | Finding force in one specific member quickly |
""")

    st.subheader("Truss Types at a Glance")
    st.markdown("""
| Type | Vertical Members | Diagonals (gravity load) |
|------|-----------------|--------------------------|
| Pratt | ✅ Yes | Tension (slope inward) |
| Howe | ✅ Yes | Compression (slope outward) |
| Warren | ❌ None | Alternating T / C |
| K-Truss | Split verticals | Long-span bridges |
| Fink | ✅ V-shaped | Common in roofs |
""")

    st.subheader("Diagrams")
    fig = diagrams.diagram_basic_truss()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ── Router ────────────────────────────────────────────────────────────────────

PAGE_MAP = {
    "home":         page_home,
    "tutorials":    page_tutorials,
    "quiz_menu":    page_quiz_menu,
    "quiz_question":page_quiz_question,
    "quiz_results": page_quiz_results,
    "achievements": page_achievements,
    "reference":    page_reference,
}

PAGE_MAP.get(st.session_state.page, page_home)()
