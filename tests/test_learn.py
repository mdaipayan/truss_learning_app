"""Unit tests for the modular interactive Learn page."""
import unittest

import learn


class LearnPageTests(unittest.TestCase):
    def test_first_topic_is_interactive_triangular_truss(self):
        fig = learn.make_topic_figure(0)
        # Three member traces plus the node trace.
        self.assertEqual(len(fig.data), 4)
        labels = [trace.name for trace in fig.data]
        self.assertIn("Bottom Chord", labels)
        self.assertIn("Left Rafter / Top Chord", labels)
        self.assertIn("Right Rafter / Top Chord", labels)
        self.assertIn("x = %{customdata[1]:.2f} m", fig.data[-1].hovertemplate)

    def test_every_existing_tutorial_has_a_plotly_figure(self):
        for index in range(6):
            with self.subTest(index=index):
                fig = learn.make_topic_figure(index)
                self.assertGreater(len(fig.data), 0)
                self.assertTrue(fig.layout.autosize)
                self.assertGreater(fig.layout.height, 0)

    def test_determinacy_and_optimization_formulas_are_latex_renderable(self):
        self.assertIn(
            ("Degree of static indeterminacy (count)", r"i=m+r-2j"),
            learn.FORMULAS["Determinacy and Stability"],
        )
        self.assertIn(
            ("Planar truss determinacy check", r"m+r=2j"),
            learn.FORMULAS["What is a Truss?"],
        )
        self.assertIn(
            ("Material-volume objective", r"\min_{\{A_i\}} V=\sum_i L_iA_i"),
            learn.FORMULAS["Determinacy and Truss Optimization"],
        )

    def test_legacy_content_tags_and_bullets_clean_up(self):
        source = "[bold cyan]A truss[/bold cyan]\n\nKey properties:\n  • Members carry axial forces"
        cleaned = learn._clean_content(source)
        self.assertNotIn("[bold", cleaned)
        self.assertIn("- Members carry axial forces", cleaned)

    def test_mobile_css_is_scoped_and_includes_breakpoint(self):
        self.assertIn(".st-key-learn_page", learn.LEARN_CSS)
        self.assertIn("@media (max-width:768px)", learn.LEARN_CSS)


if __name__ == "__main__":
    unittest.main()
