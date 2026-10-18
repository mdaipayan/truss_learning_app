"""Unit tests for the modular interactive Learn page."""
import unittest

import learn


class LearnPageTests(unittest.TestCase):
    def test_first_topic_is_interactive_triangular_truss(self):
        fig = learn.make_topic_figure(0)
        # Member, support and node traces remain individually inspectable.
        labels = [trace.name for trace in fig.data]
        self.assertIn("Bottom Chord", labels)
        self.assertIn("Left Rafter / Top Chord", labels)
        self.assertIn("Right Rafter / Top Chord", labels)
        self.assertIn("Supports", labels)
        joints = next(trace for trace in fig.data if trace.name == "Joints")
        self.assertIn("x = %{customdata[1]:.2f} m", joints.hovertemplate)
        annotation_texts = [str(item.text) for item in fig.layout.annotations]
        for label in ("P", "Ay", "Ax", "By", "4.0 m span"):
            self.assertTrue(any(label in item for item in annotation_texts), label)

    def test_every_existing_tutorial_has_a_plotly_figure(self):
        for index in range(6):
            with self.subTest(index=index):
                fig = learn.make_topic_figure(index)
                self.assertGreater(len(fig.data), 0)
                self.assertTrue(fig.layout.autosize)
                self.assertGreater(fig.layout.height, 0)


    def test_truss_types_have_clear_panel_headings(self):
        fig = learn.make_topic_figure(1)
        texts = [str(item.text) for item in fig.layout.annotations]
        for heading in ("Pratt truss", "Warren truss", "Howe truss"):
            self.assertTrue(any(heading in item for item in texts), heading)

    def test_joint_method_includes_a_free_body_diagram(self):
        fig = learn._joints_fbd_figure()
        texts = [str(item.text) for item in fig.layout.annotations]
        for label in ("Ax", "Ay", "F_AB (T)", "F_AE (T)"):
            self.assertTrue(any(label in item for item in texts), label)

    def test_section_cut_marks_three_unknown_member_forces(self):
        fig = learn.make_topic_figure(3)
        texts = [str(item.text) for item in fig.layout.annotations]
        for label in ("Section cut", "F₁", "F₂", "F₃"):
            self.assertTrue(any(label in item for item in texts), label)

    def test_determinacy_diagram_compares_all_three_cases(self):
        fig = learn.make_topic_figure(4)
        texts = [str(item.text) for item in fig.layout.annotations]
        for heading in ("DETERMINATE", "INDETERMINATE", "UNSTABLE"):
            self.assertTrue(any(heading in item for item in texts), heading)

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
