"""Responsive Home dashboard for Truss Learning.

Integration from main.py:
    import home
    home.render_home(
        progress={...},  # optional live progress dictionary
        navigate=go,     # callback accepting a route key
        tutorial_count=len(TUTORIALS),
        quiz_count=len(QUESTIONS),
    )

Navigation keys for the current single-file router:
    tutorials, solve, dsm, quiz_menu
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import streamlit as st

Progress = Mapping[str, Any]
Navigate = Callable[[str], None]

DEFAULT_PROGRESS: dict[str, Any] = {
    "rank": "Novice",
    "xp_current": 40,
    "xp_required": 100,
    "total_xp": 40,
    "streak": 0,
    "streak_unit": "Days",
    "achievements_unlocked": 1,
    "achievements_total": 10,
}

MODULES: tuple[dict[str, str], ...] = (
    {
        "key": "learn",
        "icon": "📖",
        "title": "Learn",
        "subtitle": "Interactive tutorials",
        "description": (
            "Build intuition with illustrated lessons on truss behavior, "
            "determinacy, member forces, and optimization."
        ),
        "route": "tutorials",
        "button": "Start tutorials",
    },
    {
        "key": "solve",
        "icon": "🔧",
        "title": "Solve",
        "subtitle": "Interactive truss solver",
        "description": (
            "Work through support reactions and member forces step by step, "
            "with guided hints and answer feedback."
        ),
        "route": "solve",
        "button": "Open solver",
    },
    {
        "key": "stiffness",
        "icon": "🧮",
        "title": "Stiffness Method",
        "subtitle": "Matrix math, step by step",
        "description": (
            "Explore element stiffness, global matrix assembly, boundary "
            "conditions, displacements, member forces, and reactions."
        ),
        "route": "dsm",
        "button": "Explore matrices",
    },
    {
        "key": "challenge",
        "icon": "⚔️",
        "title": "Challenge",
        "subtitle": "Quizzes and applied problems",
        "description": (
            "Test your understanding, build a correct-answer streak, and "
            "earn XP as you practice engineering concepts."
        ),
        "route": "quiz_menu",
        "button": "Take a challenge",
    },
)

HOME_CSS = r"""
<style>
/* Everything is scoped to the keyed Home container. */
.st-key-home_dashboard {
    color: #0f172a;
}
.st-key-home_dashboard .st-key-home_hero {
    padding: clamp(1.15rem, 3.2vw, 2.3rem);
    margin: 0 0 1.2rem 0;
    border: 1px solid #dbeafe;
    border-radius: 22px;
    background:
        radial-gradient(circle at 94% 8%, rgba(191,219,254,.55), transparent 34%),
        linear-gradient(135deg, #ffffff 0%, #f8fbff 68%, #eff6ff 100%);
    box-shadow: 0 8px 28px rgba(15,23,42,.045);
}
.st-key-home_dashboard .home-eyebrow {
    display: inline-block;
    margin-bottom: .65rem;
    color: #1d4ed8;
    font-size: .78rem;
    font-weight: 800;
    letter-spacing: .11em;
    text-transform: uppercase;
}
.st-key-home_dashboard .home-subtitle {
    max-width: 760px;
    margin-top: -.2rem;
    color: #475569;
    font-size: clamp(1rem, 2.2vw, 1.16rem);
    line-height: 1.65;
}
.st-key-home_dashboard .home-section-kicker {
    color: #64748b;
    font-size: .78rem;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
}
.st-key-home_dashboard .home-section-title {
    margin: .05rem 0 .3rem 0;
    color: #0f172a;
    font-size: clamp(1.18rem, 2.5vw, 1.45rem);
    font-weight: 750;
    line-height: 1.35;
}
.st-key-home_dashboard .st-key-home_stat_rank,
.st-key-home_dashboard .st-key-home_stat_xp,
.st-key-home_dashboard .st-key-home_stat_streak,
.st-key-home_dashboard .st-key-home_stat_achievements {
    height: 100%;
    padding: 1rem 1.05rem .85rem;
    border: 1px solid #e2e8f0;
    border-radius: 15px;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(15,23,42,.035);
}
.st-key-home_dashboard .st-key-home_stat_rank:hover,
.st-key-home_dashboard .st-key-home_stat_xp:hover,
.st-key-home_dashboard .st-key-home_stat_streak:hover,
.st-key-home_dashboard .st-key-home_stat_achievements:hover {
    border-color: #bfdbfe;
}
.st-key-home_dashboard .st-key-home_card_learn,
.st-key-home_dashboard .st-key-home_card_solve,
.st-key-home_dashboard .st-key-home_card_stiffness,
.st-key-home_dashboard .st-key-home_card_challenge {
    height: 100%;
    padding: 1rem 1.1rem .9rem;
    border: 1px solid #e2e8f0;
    border-radius: 17px;
    background: #ffffff;
    box-shadow: 0 3px 12px rgba(15,23,42,.04);
    transition: border-color .16s ease, box-shadow .16s ease, transform .16s ease;
}
.st-key-home_dashboard .st-key-home_card_learn:hover,
.st-key-home_dashboard .st-key-home_card_solve:hover,
.st-key-home_dashboard .st-key-home_card_stiffness:hover,
.st-key-home_dashboard .st-key-home_card_challenge:hover {
    border-color: #93c5fd;
    box-shadow: 0 9px 22px rgba(37,99,235,.10);
    transform: translateY(-2px);
}
.st-key-home_dashboard .home-card-icon {
    margin: 0 0 .3rem 0;
    font-size: 1.65rem;
    line-height: 1.3;
}
.st-key-home_dashboard .home-card-title {
    margin: 0;
    color: #0f172a;
    font-size: 1.12rem;
    font-weight: 750;
}
.st-key-home_dashboard .home-card-subtitle {
    margin: .15rem 0 .55rem 0;
    color: #1d4ed8;
    font-size: .9rem;
    font-weight: 650;
}
.st-key-home_dashboard .home-card-description {
    min-height: 4.1rem;
    margin-bottom: .8rem;
    color: #475569;
    font-size: .91rem;
    line-height: 1.55;
}
.st-key-home_dashboard .stButton > button {
    min-height: 2.7rem;
    border-radius: 10px;
    font-weight: 650;
    white-space: normal;
    overflow-wrap: anywhere;
}
.st-key-home_dashboard .stProgress > div > div > div > div {
    background-color: #2563eb;
}
.st-key-home_dashboard [data-testid="stMetricLabel"] {
    color: #64748b;
    font-size: .82rem;
    font-weight: 650;
}
.st-key-home_dashboard [data-testid="stMetricValue"] {
    color: #0f172a;
    font-weight: 750;
    overflow-wrap: anywhere;
}
.st-key-home_dashboard .home-footer-note {
    color: #64748b;
    font-size: .82rem;
    line-height: 1.5;
}
@media (max-width: 768px) {
    .st-key-home_dashboard .st-key-home_hero {
        padding: 1.1rem .9rem;
        border-radius: 16px;
    }
    .st-key-home_dashboard [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        align-items: stretch !important;
        gap: .7rem !important;
        width: 100% !important;
    }
    .st-key-home_dashboard [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    .st-key-home_dashboard .home-card-description {
        min-height: 0;
    }
    .st-key-home_dashboard .st-key-home_card_learn,
    .st-key-home_dashboard .st-key-home_card_solve,
    .st-key-home_dashboard .st-key-home_card_stiffness,
    .st-key-home_dashboard .st-key-home_card_challenge {
        padding: .9rem;
        transform: none;
    }
    .st-key-home_dashboard .stButton > button {
        min-height: 2.85rem;
        width: 100%;
    }
}
@media (prefers-reduced-motion: reduce) {
    .st-key-home_dashboard * {
        transition: none !important;
        scroll-behavior: auto !important;
    }
}
</style>
"""


def _clamp_progress(current: int, required: int) -> float:
    """Return a valid Streamlit progress fraction."""
    if required <= 0:
        return 1.0
    return min(1.0, max(0.0, current / required))


def _normalize_progress(progress: Progress | None) -> dict[str, Any]:
    """Merge live values into defaults and guard dashboard display values."""
    values = {**DEFAULT_PROGRESS, **dict(progress or {})}

    for key in (
        "xp_current",
        "xp_required",
        "total_xp",
        "streak",
        "achievements_unlocked",
        "achievements_total",
    ):
        try:
            values[key] = max(0, int(values[key]))
        except (TypeError, ValueError):
            values[key] = DEFAULT_PROGRESS[key]

    if values["achievements_total"] > 0:
        values["achievements_unlocked"] = min(
            values["achievements_unlocked"], values["achievements_total"]
        )
    else:
        values["achievements_total"] = 0
        values["achievements_unlocked"] = 0

    values["rank"] = str(values.get("rank") or "Novice")
    values["streak_unit"] = str(values.get("streak_unit") or "Days")
    values["xp_is_max_level"] = values["xp_required"] == 0
    return values


def _navigate_to(navigate: Navigate, route: str) -> None:
    """Delegate routing to the app's existing router."""
    navigate(route)


def _render_hero(navigate: Navigate) -> None:
    with st.container(key="home_hero"):
        st.markdown(
            '<div class="home-eyebrow">Your structural engineering workspace</div>',
            unsafe_allow_html=True,
        )
        st.title("Welcome to Truss Learning 🔺")
        st.markdown(
            '<div class="home-subtitle">Build engineering intuition, solve 2D trusses, '
            'explore the Direct Stiffness Method, and discover how optimization '
            'changes structural design — one interactive experiment at a time.</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        primary, secondary = st.columns([1.15, 1], gap="small")
        with primary:
            if st.button(
                "📖  Start Learning",
                type="primary",
                use_container_width=True,
                key="home_cta_start_learning",
            ):
                _navigate_to(navigate, "tutorials")
        with secondary:
            if st.button(
                "⚔️  Try a Challenge",
                use_container_width=True,
                key="home_cta_challenge",
            ):
                _navigate_to(navigate, "quiz_menu")


def _render_stats(progress: dict[str, Any]) -> None:
    st.markdown('<div class="home-section-kicker">Your progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="home-section-title">Every concept moves you forward.</div>',
                unsafe_allow_html=True)

    columns = st.columns(4, gap="small")
    stat_specs = [
        (columns[0], "home_stat_rank", "Rank / Level"),
        (columns[1], "home_stat_xp", "XP Progress"),
        (columns[2], "home_stat_streak", "Current Streak"),
        (columns[3], "home_stat_achievements", "Achievements"),
    ]

    for column, key, label in stat_specs:
        with column:
            with st.container(key=key):
                if key == "home_stat_rank":
                    st.metric(label, progress["rank"])
                    st.caption(f'{progress["total_xp"]} total XP earned')
                elif key == "home_stat_xp":
                    current = progress["xp_current"]
                    required = progress["xp_required"]
                    if required == 0:
                        st.metric(label, "MAX LEVEL")
                        st.caption(f'{progress["total_xp"]} total XP earned')
                        st.progress(1.0)
                    else:
                        st.metric(label, f"{current} / {required} XP")
                        st.caption("to the next level")
                        st.progress(_clamp_progress(current, required))
                elif key == "home_stat_streak":
                    number = progress["streak"]
                    unit = progress["streak_unit"]
                    suffix = " 🔥"
                    st.metric(label, f"{number} {unit}{suffix}")
                    st.caption("Keep your learning momentum going")
                else:
                    unlocked = progress["achievements_unlocked"]
                    total = progress["achievements_total"]
                    st.metric(label, f"{unlocked}/{total} 🏅")
                    st.caption("Milestones unlocked")


def _render_module_card(module: dict[str, str], navigate: Navigate) -> None:
    key = module["key"]
    with st.container(key=f"home_card_{key}"):
        st.markdown(
            f'<div class="home-card-icon">{module["icon"]}</div>'
            f'<div class="home-card-title">{module["title"]}</div>'
            f'<div class="home-card-subtitle">{module["subtitle"]}</div>'
            f'<div class="home-card-description">{module["description"]}</div>',
            unsafe_allow_html=True,
        )
        if st.button(
            module["button"],
            use_container_width=True,
            key=f"home_open_{key}",
        ):
            _navigate_to(navigate, module["route"])


def _render_module_grid(navigate: Navigate) -> None:
    """Render a two-column desktop grid that stacks on narrow screens."""
    for start in (0, 2):
        columns = st.columns(2, gap="medium")
        for column, module in zip(columns, MODULES[start:start + 2]):
            with column:
                _render_module_card(module, navigate)


def render_home(
    *,
    progress: Progress | None = None,
    navigate: Navigate,
    tutorial_count: int = 6,
    quiz_count: int = 17,
) -> None:
    """Render the landing dashboard.

    Parameters
    ----------
    progress:
        Optional mapping with rank, xp_current, xp_required, total_xp, streak,
        streak_unit, achievements_unlocked and achievements_total. Without it,
        example values are shown for previews.
    navigate:
        Required callback that accepts a route key and delegates to the app's
        navigation function (for example, main.py's go).
    tutorial_count:
        Number of currently available tutorials.
    quiz_count:
        Number of currently available quiz questions.
    """
    if not callable(navigate):
        raise TypeError("render_home requires a navigate(route) callback.")

    stats = _normalize_progress(progress)
    with st.container(key="home_dashboard"):
        st.markdown(HOME_CSS, unsafe_allow_html=True)
        _render_hero(navigate)
        st.write("")
        _render_stats(stats)
        _render_modules(navigate)
        st.write("")
        st.markdown(
            f'<div class="home-footer-note">📚 {int(tutorial_count)} tutorials'
            f' &nbsp;·&nbsp; ⚔️ {int(quiz_count)} quiz questions'
            ' &nbsp;·&nbsp; Learn at your own pace. Build real engineering intuition.</div>',
            unsafe_allow_html=True,
        )
