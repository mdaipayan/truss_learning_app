"""Unit tests for the reusable Home dashboard helpers."""
import unittest

import home


class HomeDashboardTests(unittest.TestCase):
    def test_preview_defaults_match_requested_dashboard(self):
        values = home._normalize_progress(None)
        self.assertEqual(values["rank"], "Novice")
        self.assertEqual(values["xp_current"], 40)
        self.assertEqual(values["xp_required"], 100)
        self.assertEqual(values["streak"], 0)
        self.assertEqual(values["streak_unit"], "Days")
        self.assertEqual(values["achievements_unlocked"], 1)
        self.assertEqual(values["achievements_total"], 10)

    def test_live_progress_overrides_preview_values(self):
        values = home._normalize_progress({
            "rank": "Apprentice",
            "xp_current": 25,
            "xp_required": 150,
            "total_xp": 125,
            "streak": 4,
            "streak_unit": "correct in a row",
            "achievements_unlocked": 3,
            "achievements_total": 10,
        })
        self.assertEqual(values["rank"], "Apprentice")
        self.assertEqual(values["xp_current"], 25)
        self.assertEqual(values["total_xp"], 125)
        self.assertEqual(values["streak_unit"], "correct in a row")
        self.assertEqual(values["achievements_unlocked"], 3)

    def test_invalid_or_out_of_range_values_are_sanitized(self):
        values = home._normalize_progress({
            "xp_current": -9,
            "xp_required": 0,
            "streak": "not a number",
            "achievements_unlocked": 50,
            "achievements_total": 10,
        })
        self.assertEqual(values["xp_current"], 0)
        self.assertEqual(values["streak"], 0)
        self.assertEqual(values["achievements_unlocked"], 10)
        self.assertEqual(values["xp_is_max_level"], True)
        self.assertEqual(home._clamp_progress(0, 0), 1.0)
        self.assertEqual(home._clamp_progress(200, 100), 1.0)
        self.assertEqual(home._clamp_progress(-1, 100), 0.0)

    def test_module_routes_match_main_router(self):
        self.assertEqual(
            [module["route"] for module in home.MODULES],
            ["tutorials", "solve", "dsm", "quiz_menu"],
        )
        self.assertEqual(len(home.MODULES), 4)


if __name__ == "__main__":
    unittest.main()
