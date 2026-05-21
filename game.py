"""Game state: XP, levels, achievements, persistence."""
import json, os
from typing import Set, List

SAVE_FILE = "/tmp/truss_save.json"

LEVELS = [
    {"name": "Novice",       "icon": "🔩", "min_xp": 0},
    {"name": "Apprentice",   "icon": "⚙️",  "min_xp": 100},
    {"name": "Technician",   "icon": "🔧", "min_xp": 250},
    {"name": "Engineer",     "icon": "🏗️",  "min_xp": 500},
    {"name": "Master",       "icon": "🏆", "min_xp": 1000},
]

ACHIEVEMENTS = [
    {"id": "first_tutorial",  "icon": "🌱", "name": "First Steps",
     "desc": "Read your first tutorial",          "xp": 25},
    {"id": "all_tutorials",   "icon": "📚", "name": "Scholar",
     "desc": "Read all 5 tutorials",              "xp": 50},
    {"id": "first_correct",   "icon": "🎯", "name": "First Try",
     "desc": "Answer your first question correctly","xp": 15},
    {"id": "streak_3",        "icon": "🔥", "name": "On Fire",
     "desc": "Get 3 correct answers in a row",    "xp": 30},
    {"id": "streak_5",        "icon": "⚡", "name": "Lightning",
     "desc": "Get 5 correct answers in a row",    "xp": 50},
    {"id": "perfect_score",   "icon": "🏅", "name": "Flawless",
     "desc": "Score 100% on any quiz",            "xp": 75},
    {"id": "full_quiz",       "icon": "🎓", "name": "Graduate",
     "desc": "Complete a full all-topics quiz",   "xp": 40},
    {"id": "topic_quiz",      "icon": "🔬", "name": "Specialist",
     "desc": "Complete a topic-specific quiz",    "xp": 30},
    {"id": "q25",             "icon": "💪", "name": "Persistent",
     "desc": "Answer 25 questions total",         "xp": 60},
    {"id": "master_level",    "icon": "🏆", "name": "Master Engineer",
     "desc": "Reach the Master level",            "xp": 100},
]

ACH_MAP = {a["id"]: a for a in ACHIEVEMENTS}


def _make_state():
    return {
        "xp": 0,
        "tutorials_read": [],
        "total_answered": 0,
        "total_correct": 0,
        "best_streak": 0,
        "unlocked": [],
    }


def load() -> dict:
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            # Ensure all keys exist (forward compat)
            base = _make_state()
            base.update(data)
            return base
        except Exception:
            pass
    return _make_state()


def save(state: dict):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def get_level(xp: int) -> dict:
    level = LEVELS[0]
    for lv in LEVELS:
        if xp >= lv["min_xp"]:
            level = lv
    return level


def get_level_index(xp: int) -> int:
    idx = 0
    for i, lv in enumerate(LEVELS):
        if xp >= lv["min_xp"]:
            idx = i
    return idx


def xp_to_next_level(xp: int) -> tuple[int, int]:
    """Returns (xp_in_current_band, band_size). Both 0 if at max level."""
    idx = get_level_index(xp)
    if idx >= len(LEVELS) - 1:
        return 0, 0
    current_min = LEVELS[idx]["min_xp"]
    next_min    = LEVELS[idx + 1]["min_xp"]
    return xp - current_min, next_min - current_min


def check_achievements(state: dict, streak: int, quiz_topic: str | None, quiz_total: int | None) -> list[dict]:
    """Return list of newly unlocked achievements (with xp) given updated state."""
    already = set(state["unlocked"])
    new = []

    def _unlock(aid):
        if aid not in already:
            new.append(ACH_MAP[aid])
            already.add(aid)

    if state["tutorials_read"]:
        _unlock("first_tutorial")
    if len(state["tutorials_read"]) >= 5:
        _unlock("all_tutorials")
    if state["total_correct"] >= 1:
        _unlock("first_correct")
    if streak >= 3:
        _unlock("streak_3")
    if streak >= 5:
        _unlock("streak_5")
    if state["total_answered"] >= 25:
        _unlock("q25")
    if get_level_index(state["xp"]) >= len(LEVELS) - 1:
        _unlock("master_level")
    if quiz_topic == "All topics" and quiz_total is not None:
        _unlock("full_quiz")
    if quiz_topic not in (None, "All topics") and quiz_total is not None:
        _unlock("topic_quiz")
    if quiz_total is not None and state["total_correct"] == state["total_answered"]:
        _unlock("perfect_score")

    state["unlocked"] = list(already)
    for a in new:
        state["xp"] += a["xp"]
    return new
