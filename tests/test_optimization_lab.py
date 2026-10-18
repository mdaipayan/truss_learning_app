"""Regression tests for the determinacy/optimization lesson."""
import unittest

import numpy as np

import optimization_lab as lab


class TrussOptimizationTests(unittest.TestCase):
    def test_determinacy_counts(self):
        determinate = lab.solve_design(redundant=False)
        indeterminate = lab.solve_design(redundant=True)
        self.assertEqual(determinate["determinacy_index"], 0)
        self.assertEqual(indeterminate["determinacy_index"], 1)
        self.assertEqual(determinate["count_members"], 5)
        self.assertEqual(indeterminate["count_members"], 6)

    def test_determinate_member_forces_do_not_depend_on_areas(self):
        base = lab.solve_design(
            redundant=False, areas_mm2=[800, 800, 800, 800, 800]
        )
        varied = lab.solve_design(
            redundant=False, areas_mm2=[300, 450, 900, 1200, 700]
        )
        forces_base = np.array([m["force_kN"] for m in base["members"]])
        forces_varied = np.array([m["force_kN"] for m in varied["members"]])
        np.testing.assert_allclose(forces_base, forces_varied, atol=1e-6, rtol=1e-6)

    def test_redundant_member_stiffness_changes_force_sharing(self):
        areas = [800.0] * 6
        low_e = lab.solve_design(
            True, areas,
            member_moduli_gpa=[200.0] * 5 + [100.0],
        )
        high_e = lab.solve_design(
            True, areas,
            member_moduli_gpa=[200.0] * 5 + [300.0],
        )
        f_low = np.array([m["force_kN"] for m in low_e["members"]])
        f_high = np.array([m["force_kN"] for m in high_e["members"]])
        self.assertGreater(float(np.max(np.abs(f_low - f_high))), 1e-3)

    def test_same_cd_ea_gives_same_linear_elastic_force_solution(self):
        case_a = lab.solve_design(
            True, [800.0] * 6,
            member_moduli_gpa=[200.0] * 5 + [200.0],
        )
        case_b = lab.solve_design(
            True, [800.0] * 5 + [1600.0],
            member_moduli_gpa=[200.0] * 5 + [100.0],
        )
        forces_a = np.array([m["force_kN"] for m in case_a["members"]])
        forces_b = np.array([m["force_kN"] for m in case_b["members"]])
        np.testing.assert_allclose(forces_a, forces_b, atol=1e-6, rtol=1e-6)

    def test_default_optimizations_are_feasible(self):
        for redundant in (False, True):
            with self.subTest(redundant=redundant):
                result = lab.optimize_design(
                    redundant=redundant,
                    load_each_kN=50.0,
                    allowable_stress_mpa=150.0,
                    max_displacement_mm=4.0,
                )
                self.assertTrue(result["feasible"], result["optimization_message"])
                self.assertLessEqual(
                    result["max_displacement_mm"], 4.0 + 1e-3
                )
                self.assertLessEqual(
                    max(abs(m["stress_MPa"]) for m in result["members"]),
                    150.0 + 1e-3,
                )

    def test_plotting_includes_force_and_deformation_layers(self):
        response = lab.solve_design(redundant=True)
        original = lab.plot_truss_plotly(response, redundant=True)
        deformed = lab.plot_truss_plotly(
            response, redundant=True, show_deflected=True, exaggeration=50
        )
        self.assertEqual(len(original.data), len(response["members"]) + 1)
        self.assertEqual(len(deformed.data), len(response["members"]) + 2)

    def test_member_report_has_utilization(self):
        response = lab.solve_design(redundant=True)
        report = lab.member_report(response, allowable_stress_mpa=150.0)
        self.assertEqual(len(report), 6)
        self.assertIn("Utilization |σ|/σallow", report.columns)
        self.assertTrue((report["Utilization |σ|/σallow"] >= 0).all())


if __name__ == "__main__":
    unittest.main()
