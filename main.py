"""Truss Learning App — Streamlit web interface."""

import random
import streamlit as st
from questions import TUTORIALS, QUESTIONS

st.set_page_config(page_title="Truss Learning App", page_icon="🔺", layout="wide")

# ── Session state defaults ────────────────────────────────────────────────────

def _init_state():
    defaults = {
        "page": "home",
        "tutorial_idx": 0,
        "quiz_pool": None,
        "quiz_idx": 0,
        "quiz_score": 0,
        "quiz_wrong": [],
        "quiz_answered": False,
        "quiz_selected": None,
        "quiz_topic": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


def go(page, **kwargs):
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


# ── Sidebar nav ───────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🔺 Truss Learning")
    st.divider()
    if st.button("🏠 Home", use_container_width=True):
        go("home")
    if st.button("📖 Tutorials", use_container_width=True):
        go("tutorials")
    if st.button("📝 Quiz", use_container_width=True):
        go("quiz_menu")
    if st.button("📋 Reference Card", use_container_width=True):
        go("reference")
    st.divider()
    st.caption("Structural analysis fundamentals")


# ── Home ──────────────────────────────────────────────────────────────────────

def page_home():
    st.title("🔺 Truss Learning App")
    st.subheader("Structural analysis fundamentals")
    st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 📖 Tutorials\nLearn truss concepts step by step — from basics to analysis methods.")
        if st.button("Start Tutorials", use_container_width=True):
            go("tutorials")
    with col2:
        st.success("### 📝 Quiz\nTest your knowledge with 13 questions across 5 topics.")
        if st.button("Take a Quiz", use_container_width=True):
            go("quiz_menu")
    with col3:
        st.warning("### 📋 Reference Card\nKey formulas and zero-force-member rules at a glance.")
        if st.button("View Reference", use_container_width=True):
            go("reference")

    st.divider()
    st.markdown("""
**Topics covered:**
- What is a truss? (members, joints, assumptions)
- Types of trusses (Pratt, Warren, Howe, K-Truss, Fink)
- Method of Joints — step-by-step analysis
- Method of Sections — cutting plane technique
- Determinacy & Stability — m + r = 2j
""")


# ── Tutorials ─────────────────────────────────────────────────────────────────

def page_tutorials():
    st.title("📖 Tutorials")

    # Topic selector in sidebar area — use radio
    topics = [t["title"] for t in TUTORIALS]
    idx = st.session_state.tutorial_idx

    selected = st.radio("Select a topic:", topics, index=idx, key="tutorial_radio")
    new_idx = topics.index(selected)
    if new_idx != idx:
        st.session_state.tutorial_idx = new_idx
        idx = new_idx

    st.divider()

    t = TUTORIALS[idx]
    st.subheader(f"{idx + 1}. {t['title']}")
    st.caption(f"Topic {idx + 1} of {len(TUTORIALS)}")

    # Strip Rich markup tags for plain display
    import re
    content = re.sub(r'\[/?[^\]]+\]', '', t["content"])
    st.markdown(content)

    st.divider()
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if idx > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.tutorial_idx = idx - 1
                st.rerun()
    with col_next:
        if idx < len(TUTORIALS) - 1:
            if st.button("Next →", use_container_width=True):
                st.session_state.tutorial_idx = idx + 1
                st.rerun()


# ── Quiz menu ─────────────────────────────────────────────────────────────────

def page_quiz_menu():
    st.title("📝 Quiz")
    st.write("Choose a quiz mode to get started.")
    st.write("")

    topics = sorted({q["topic"] for q in QUESTIONS})

    col1, col2 = st.columns([1, 2])
    with col1:
        mode = st.radio("Quiz mode:", ["All topics"] + topics)

    with col2:
        topic_counts = {t: sum(1 for q in QUESTIONS if q["topic"] == t) for t in topics}
        total = len(QUESTIONS)
        if mode == "All topics":
            st.metric("Questions", total)
            st.caption("Covers: " + ", ".join(topics))
        else:
            st.metric("Questions", topic_counts[mode])
            st.caption(f"Topic: {mode}")

    st.write("")
    if st.button("▶ Start Quiz", type="primary", use_container_width=False):
        if mode == "All topics":
            pool = QUESTIONS[:]
        else:
            pool = [q for q in QUESTIONS if q["topic"] == mode]
        random.shuffle(pool)
        st.session_state.quiz_pool = pool
        st.session_state.quiz_idx = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_wrong = []
        st.session_state.quiz_answered = False
        st.session_state.quiz_selected = None
        st.session_state.quiz_topic = mode
        go("quiz_question")


# ── Quiz question ─────────────────────────────────────────────────────────────

def page_quiz_question():
    pool = st.session_state.quiz_pool
    idx = st.session_state.quiz_idx

    if idx >= len(pool):
        go("quiz_results")

    q = pool[idx]
    answered = st.session_state.quiz_answered
    selected = st.session_state.quiz_selected

    # Progress
    progress = (idx) / len(pool)
    st.progress(progress, text=f"Question {idx + 1} of {len(pool)}  —  Score: {st.session_state.quiz_score}/{idx}")

    st.subheader(f"Q{idx + 1}. {q['question']}")
    st.caption(f"Topic: {q['topic']}")
    st.write("")

    # Answer buttons
    for i, opt in enumerate(q["options"]):
        if answered:
            if i == q["answer"]:
                st.success(f"✓  {opt}")
            elif i == selected:
                st.error(f"✗  {opt}")
            else:
                st.button(opt, key=f"opt_{i}", disabled=True)
        else:
            if st.button(opt, key=f"opt_{i}", use_container_width=True):
                st.session_state.quiz_selected = i
                st.session_state.quiz_answered = True
                if i == q["answer"]:
                    st.session_state.quiz_score += 1
                else:
                    st.session_state.quiz_wrong.append(q)
                st.rerun()

    # Feedback
    if answered:
        st.write("")
        if selected == q["answer"]:
            st.success("**Correct!**")
        else:
            st.error(f"**Incorrect.** The correct answer was: _{q['options'][q['answer']]}_")
        st.info(f"💡 {q['explanation']}")
        st.write("")
        if st.button("Next Question →" if idx + 1 < len(pool) else "See Results →", type="primary"):
            st.session_state.quiz_idx = idx + 1
            st.session_state.quiz_answered = False
            st.session_state.quiz_selected = None
            st.rerun()


# ── Quiz results ──────────────────────────────────────────────────────────────

def page_quiz_results():
    score = st.session_state.quiz_score
    total = len(st.session_state.quiz_pool)
    wrong = st.session_state.quiz_wrong
    pct = score / total * 100

    st.title("📊 Quiz Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score} / {total}")
    col2.metric("Percentage", f"{pct:.0f}%")
    col3.metric("Incorrect", len(wrong))

    st.progress(score / total)

    st.write("")
    if pct == 100:
        st.success("🎉 Perfect score! Outstanding work.")
    elif pct >= 75:
        st.success("👍 Great job! Review the topics you missed.")
    elif pct >= 50:
        st.warning("📚 Good effort. Work through the tutorials on the topics below.")
    else:
        st.error("🔁 More study needed. Review the tutorials and try again.")

    if wrong:
        st.write("")
        st.subheader("Topics to review:")
        reviewed = set()
        for q in wrong:
            if q["topic"] not in reviewed:
                st.write(f"- **{q['topic']}**")
                reviewed.add(q["topic"])

    st.write("")
    col_retry, col_menu, col_tutorials = st.columns(3)
    with col_retry:
        if st.button("🔁 Retry same quiz", use_container_width=True):
            pool = st.session_state.quiz_pool[:]
            random.shuffle(pool)
            st.session_state.quiz_pool = pool
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_wrong = []
            st.session_state.quiz_answered = False
            st.session_state.quiz_selected = None
            go("quiz_question")
    with col_menu:
        if st.button("📝 New quiz", use_container_width=True):
            go("quiz_menu")
    with col_tutorials:
        if st.button("📖 Go to tutorials", use_container_width=True):
            go("tutorials")


# ── Reference card ────────────────────────────────────────────────────────────

def page_reference():
    st.title("📋 Quick Reference Card")
    st.caption("Key formulas and rules for planar truss analysis")
    st.write("")

    st.subheader("Determinacy")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
| Condition | Classification |
|-----------|---------------|
| m + r = 2j | Statically determinate ✓ |
| m + r < 2j | Unstable (mechanism) ✗ |
| m + r > 2j | Statically indeterminate |
""")
    with col2:
        st.info("**Variables**\n\nm = number of members\n\nr = number of external reaction components\n\nj = number of joints")

    st.subheader("Method of Joints")
    st.markdown("""
| Rule | Detail |
|------|--------|
| Equilibrium equations | ΣFx = 0,  ΣFy = 0 per joint |
| Starting joint | At most **2 unknown members** |
| Sign convention | Assume tension; negative result → compression |
| Zero-force (2 members, no load, non-collinear) | Both members are zero-force |
| Zero-force (3 members, 2 collinear, no load) | Third member is zero-force |
""")

    st.subheader("Method of Sections")
    st.markdown("""
| Rule | Detail |
|------|--------|
| Equilibrium equations | ΣFx = 0,  ΣFy = 0,  ΣM = 0 for cut section |
| Maximum cut members | **3 unknowns** per cut |
| Best moment point | Intersection of the other two unknown forces |
| Best use case | Finding force in one or a few specific members quickly |
""")

    st.subheader("Truss Types at a Glance")
    st.markdown("""
| Type | Key Feature | Diagonals under typical load |
|------|-------------|------------------------------|
| Pratt | Verticals in compression | Tension |
| Howe | Verticals in tension | Compression |
| Warren | No verticals | Alternating T/C |
| K-Truss | Diagonals meet vertical at mid-height | Long-span bridges |
| Fink | V-shaped sub-triangles | Common in roofs |
""")


# ── Router ────────────────────────────────────────────────────────────────────

page = st.session_state.page
if page == "home":
    page_home()
elif page == "tutorials":
    page_tutorials()
elif page == "quiz_menu":
    page_quiz_menu()
elif page == "quiz_question":
    page_quiz_question()
elif page == "quiz_results":
    page_quiz_results()
elif page == "reference":
    page_reference()
