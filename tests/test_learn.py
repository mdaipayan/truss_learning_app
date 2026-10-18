"""Unit tests for the modular interactive Learn page."""
import unittest

import learn
from questions import QUESTIONS, TUTORIALS


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
        for index in range(10):
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


    def test_three_uploaded_study_note_topics_are_appended(self):
        titles = [item["title"] for item in TUTORIALS]
        self.assertEqual(len(TUTORIALS), 10)
        for title in (
            "Determinate Truss: Force, Stress and Displacement",
            "Indeterminate Triangle: Redundant Reaction",
            "Internal Redundancy: Force Method",
        ):
            self.assertIn(title, titles)
        new_topics = {
            "Determinate vs Indeterminate",
            "Indeterminate Triangle",
            "Force Method",
            "Compatibility and Load Sharing",
        }
        self.assertTrue(new_topics.issubset({item["topic"] for item in QUESTIONS}))

    def test_indeterminate_triangle_area_cases_match_uploaded_notes(self):
        equal = learn._small_indeterminate_response([1000, 1000, 1000])
        self.assertAlmostEqual(equal["R"], -16.6666667, places=5)
        self.assertAlmostEqual(equal["N_AB"], 3.3333333, places=5)
        self.assertAlmostEqual(equal["N_AC"], -17.5, places=5)
        self.assertAlmostEqual(equal["N_BC"], -4.1666667, places=5)

        larger_bc = learn._small_indeterminate_response([1000, 1000, 2000])
        self.assertAlmostEqual(larger_bc["R"], -15.30944, places=3)
        self.assertAlmostEqual(larger_bc["N_AB"], 4.69056, places=3)
        self.assertGreater(larger_bc["N_AC"], equal["N_AC"])  # less compression magnitude

    def test_new_diagrams_use_uploaded_geometries_and_labels(self):
        determinate = learn.make_topic_figure(6)
        texts = [str(item.text) for item in determinate.layout.annotations]
        self.assertTrue(any("Px = 20 kN" in item for item in texts))
        self.assertTrue(any("AB: 20 kN tension" in item for item in texts))

        redundant_triangle = learn.make_topic_figure(7)
        texts = [str(item.text) for item in redundant_triangle.layout.annotations]
        self.assertTrue(any("R = Cx" in item for item in texts))
        self.assertTrue(any("m + r − 2j = 1" in item for item in texts))

        double_diagonal = learn.make_topic_figure(8)
        labels = [trace.name for trace in double_diagonal.data]
        self.assertTrue(any("BD — selected redundant" in label for label in labels))
        self.assertGreater(len(double_diagonal.layout.shapes), 0)

    def test_force_method_arithmetic_discrepancy_is_not_silently_hidden(self):
        # Listed terms in the uploaded PDF sum to 12,280 mm, not the printed 13,400 mm.
        total = (
            0.8**2 * 4000 + 0.6**2 * 3000
            + 0.8**2 * 4000 + 0.6**2 * 3000 + 1.0**2 * 5000
        )
        self.assertEqual(total, 12280)
        lesson = next(item for item in TUTORIALS
                      if item["title"] == "Internal Redundancy: Force Method")
        self.assertIn("12280", lesson["content"])
        self.assertIn("instructor verification", lesson["content"])


    def test_parallel_bar_load_sharing_matches_uploaded_cases(self):
        force1, force2 = learn._parallel_bar_forces(1000, 2000)
        self.assertAlmostEqual(force1, 33.3333333, places=5)
        self.assertAlmostEqual(force2, 66.6666667, places=5)
        self.assertAlmostEqual(force1 + force2, 100.0, places=8)

        force1, force2 = learn._parallel_bar_forces(1000, 4000)
        self.assertAlmostEqual(force1, 20.0, places=8)
        self.assertAlmostEqual(force2, 80.0, places=8)

    def test_parallel_bar_diagram_and_formula_cards_are_present(self):
        fig = learn.make_topic_figure(9)
        annotation_text = [str(item.text) for item in fig.layout.annotations]
        self.assertTrue(any("P = 100 kN" in item for item in annotation_text))
        self.assertTrue(any("δ1 = δ2" in item for item in annotation_text))
        self.assertIn(
            ("Load-sharing ratio", r"\frac{F_1}{F_2}=\frac{k_1}{k_2}"),
            learn.FORMULAS["Parallel Bars: Compatibility and Load Sharing"],
        )

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
            "Steps:\n"
            "  1. Find support reactions.\n"
            "  2. Start at a joint.\n"
            "Key properties:\n"
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
