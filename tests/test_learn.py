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

    def test_legacy_markup_becomes_semantic_color_highlights(self):
        source = (
            "[bold cyan]Truss member[/bold cyan] carries "
            "[yellow]axial force[/yellow]. "
            "[green]Tension[/green] is positive; "
            "[red]compression[/red] is negative."
        )
        cleaned = learn._clean_content(source)
        self.assertIn('<span class="learn-concept">Truss member</span>', cleaned)
        self.assertIn('<mark class="learn-highlight">axial force</mark>', cleaned)
        self.assertIn('<span class="learn-positive">Tension</span>', cleaned)
        self.assertIn('<span class="learn-warning">compression</span>', cleaned)
        self.assertNotIn("[bold cyan]", cleaned)

    def test_equations_are_highlighted_and_less_than_is_html_safe(self):
        cleaned = learn._clean_content("The count rule is m + r < 2j.")
        self.assertIn('<span class="learn-equation">m + r &lt; 2j</span>', cleaned)

    def test_section_labels_become_headings_and_bullets_remain_bullets(self):
        source = (
            "Steps:\\n"
            "  1. Find support reactions.\\n"
            "  2. Start at a joint.\\n"
            "Key properties:\\n"
            "  • Loads act at joints."
        )
        cleaned = learn._clean_content(source)
        self.assertIn("#### 🧭 Step-by-step method", cleaned)
        self.assertIn("1. Find support reactions.", cleaned)
        self.assertIn("#### 🔑 Key properties", cleaned)
        self.assertIn("- Loads act at joints.", cleaned)

    def test_theory_highlight_styles_are_scoped_and_defined(self):
        for class_name in (
            "learn-concept", "learn-highlight", "learn-positive",
            "learn-warning", "learn-equation",
        ):
            self.assertIn(class_name, learn.LEARN_CSS)
        self.assertIn(".st-key-learn_theory_panel h4", learn.LEARN_CSS)


    def test_mobile_css_is_scoped_and_includes_breakpoint(self):
        self.assertIn(".st-key-learn_page", learn.LEARN_CSS)
        self.assertIn("@media (max-width:768px)", learn.LEARN_CSS)


if __name__ == "__main__":
    unittest.main()
