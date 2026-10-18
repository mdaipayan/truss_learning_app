# Task Plan — Truss Learning Refactor

Use this checklist as the implementation roadmap for the AI coding assistant. Check items only when there is evidence: an updated file, a passing test, a successful CI run, or a documented manual verification. Do not mark browser/mobile checks complete because code compiles.

## Phase 0 — Establish the baseline

- [x] Identify the current app entry point and top-level modules.
- [x] Identify the tutorial, quiz, game/progress, diagram, solver and optimization modules.
- [x] Record the supported dependencies in requirements.txt.
- [x] Add a Python CI workflow that compiles Python files and runs numerical regression tests.
- [ ] Capture the current branch, commit SHA, Python version, dependency versions and CI result in memory.md before substantial future work.
- [ ] Create a reproducible baseline screenshot set for Home, Learn, Solve, DSM, Quiz and the optimization lab.

**Exit criteria:** The assistant can explain where a requested behavior belongs and how it will be tested.

## Phase 1 — Verify numerical model correctness

- [x] Document the node/member topology, support conditions and load cases used by optimization_lab.py.
- [x] Document the units used for E, A, L, P, displacement, stress and volume.
- [x] Test the determinate and redundant member-count indices.
- [x] Test that forces in the determinate model are invariant when only member areas change, under the same geometry and loading.
- [x] Test that the redundant model's force distribution can change when the added member's relative EA/L changes.
- [x] Test the equivalent linear-elastic EA/L case.
- [x] Test the member report's utilization calculations and expected row count.
- [x] Test the default optimization cases for feasibility under their selected constraints.
- [ ] Independently hand-check at least one force/displacement case and record the calculation in a test or verification note.
- [ ] Add tests for a known singular/unstable geometry, invalid area/modulus/load, and infeasible constraint combinations.
- [ ] Add explicit stability/rank diagnostics beyond the counting index.
- [ ] Review solver sign conventions, support reactions, units, tolerances and displacement norms.
- [ ] Confirm that changing a member modulus affects stiffness only and does not implicitly change any other material property.

**Exit criteria:** Numerical functions return transparent results, invalid cases are handled deliberately, and critical calculations have independent regression checks.

## Phase 2 — Establish clean modular boundaries

- [x] Keep UI orchestration in main.py and optimization-lab calculations/UI in optimization_lab.py.
- [x] Keep tutorial content and quiz prompts in questions.py.
- [x] Keep Matplotlib diagrams in diagrams.py and worked solver steps in solver.py.
- [ ] Review for duplicate DSM implementations or duplicated constraint calculations.
- [ ] Extract a separate pure analysis module only if optimization_lab.py becomes difficult to test or reason about; do not add abstractions solely for their own sake.
- [ ] Define result types for analysis and optimization if that makes result keys and optional fields clearer.
- [ ] Confirm UI rendering code is not silently altering the model inputs.

**Exit criteria:** One authoritative implementation exists for each calculation and each result field has a documented meaning and unit.

## Phase 3 — Responsive UI and accessibility

- [x] Extract the Home dashboard into reusable home.py with an injected navigation callback and live progress data.
- [x] Add the hero CTA, gamification metrics, XP progress bar, four module cards, and scoped card/hover CSS.
- [x] Add unit tests for Home defaults, live progress normalization, safe metric values and route mapping.
- [x] Require a Streamlit version with keyed containers for component-scoped CSS.
- [x] Keep Streamlit's wide page layout.
- [x] Add a CSS breakpoint at 768px to wrap/stack horizontal content and reduce mobile padding.
- [x] Add mobile styles for metric values, table containment, touch targets, tab overflow and wrapping radio groups.
- [x] Replace the tutorial-topic horizontal radio group with a selectbox.
- [x] Group optimization parameters in an expander.
- [ ] Open every main page at 360px, 390px, 768px, 1024px and 1440px widths.
- [ ] Verify the sidebar does not stay in the way on small screens; use automatic/collapsed behavior where supported.
- [ ] Check for horizontal page overflow, clipped equation text, hidden buttons and chart clipping.
- [ ] Confirm all important controls work with touch and keyboard navigation.
- [ ] Confirm focus states and contrast are legible.
- [ ] Check the visual behavior after a Streamlit version change; revise CSS selectors if its internal DOM has changed.
- [ ] Check browser zoom at 200% and a high system text size.
- [ ] Record screenshots and issues rather than relying on memory.

**Exit criteria:** No important action is hidden or clipped on phone, tablet or desktop; desktop layouts remain balanced.

## Phase 4 — Interactive truss visualization

- [x] Add Plotly force mapping with red compression, blue tension and gray zero-force members.
- [x] Scale line width by absolute axial force and provide utilization in hover text.
- [x] Add a “Show Deflected Shape” toggle.
- [x] Add a 10×–100× deformation-exaggeration slider.
- [x] Draw the undeformed mesh as dashed gray lines when the overlay is enabled.
- [x] Make Plotly charts responsive and set concise margins.
- [x] Add a current-force plot to the stiffness sensitivity experiment.
- [ ] Verify deformation coordinates and axis units manually using a known displacement example.
- [ ] Check that chart scaling communicates the exaggeration factor and does not imply the deformation is to scale.
- [ ] Confirm color, line width and hover text remain discernible at phone width and in grayscale/low-contrast environments.
- [ ] Avoid a chart if the solver response is invalid; render a clear message instead.
- [ ] Benchmark redraw time for typical and high-frequency slider changes.

**Exit criteria:** Students can see undeformed and deflected configurations, identify force types, and inspect useful numeric details without horizontal scrolling.

## Phase 5 — Optimization, sensitivity and result communication

- [x] Add sensitivity mode selection between CD cross-sectional area A and Young's modulus E.
- [x] Display the current CD axial stiffness EA/L with units.
- [x] Recalculate forces for the sensitivity experiment.
- [x] Add the material-volume optimization for determinate and redundant layouts.
- [x] Show optimizer feasibility, volume, maximum displacement and maximum absolute stress.
- [x] Add member tables with L, A, P, stress, utilization and force type.
- [x] Highlight utilization greater than 1.0 and report overstress clearly.
- [x] Add formula cards for i = m + r − 2j and the sizing objective/constraints.
- [x] Explain that indeterminacy alone does not guarantee lower volume.
- [ ] Check behavior when the optimizer fails, constraints are infeasible, or some areas reach their lower/upper bounds.
- [ ] Confirm comparisons are shown as a direct insight only when both designs are feasible.
- [ ] Add a concise list of active constraints and indicate which constraint is governing, if feasible and maintainable.
- [ ] Test slider changes at minimum, default and maximum values.
- [ ] Review whether the chosen displacement constraint should be maximum resultant nodal displacement or a user-selectable vertical/horizontal serviceability limit. Document the selected definition.
- [ ] Add a buckling constraint only with a clearly documented model, member effective-length assumptions, and appropriate validation; never present axial stress alone as a complete steel-member check.

**Exit criteria:** The user can reproduce the reported results, understand the binding constraints, and distinguish solver convergence from feasibility.

## Phase 6 — Educational experience

- [x] Add the determinacy-and-optimization tutorial and associated quiz questions.
- [x] Explain that m + r = 2j is a counting check, not proof of stability.
- [x] Explain force redistribution through compatibility and relative EA/L.
- [ ] Add a short “predict before you adjust” prompt for the sensitivity experiment.
- [ ] Provide a concise post-experiment reflection: what changed, why it changed, and which observation distinguishes determinate from redundant behavior.
- [ ] Add unit hints, definitions on hover, and a glossary for novice users.
- [ ] Provide worked examples with hand-calculated values next to the numerical solution.
- [ ] Confirm tutorial XP is awarded only once and new quiz topics appear in all appropriate menu/result views.
- [ ] Have a civil-engineering instructor review wording, notation and the engineering assumptions.

**Exit criteria:** A novice student can follow the lesson and explain the physical reason behind the results, not just manipulate sliders.

## Phase 7 — State and persistence

- [x] Use a session-scoped save key instead of a single shared progress file.
- [ ] State clearly that temporary session files do not guarantee persistent progress.
- [ ] Decide whether the product needs authenticated student identities, class/instructor workflows, and durable progress.
- [ ] If required, design persistent storage (e.g., a database) and access controls before implementing student records.
- [ ] Test two concurrent sessions and verify that neither can overwrite the other's progress.
- [ ] Test reconnects/restarts to document what persists and what is reset.

**Exit criteria:** Progress guarantees match actual storage behavior; no student can access another student's records.

## Phase 8 — Automated and manual quality gates

- [x] Add GitHub Actions to install requirements, compile Python files and run unittest discovery.
- [x] Add regression tests for determinacy, force sensitivity, optimization feasibility, plotting and utilization reporting.
- [ ] Run the workflow on the final candidate commit and inspect its exact SHA and conclusion.
- [ ] Run the full local test suite in a clean environment matching CI.
- [ ] Test app startup and every main navigation path manually.
- [ ] Validate expected exceptions and infeasible design messages.
- [ ] Review the full Git diff and check for accidental changes to unrelated functionality.
- [ ] Run a security/dependency review; do not commit secrets, API tokens, private student data or environment files.
- [ ] Keep warnings actionable and avoid exposing raw traces to students.

**Exit criteria:** CI is green on the final commit, manual smoke tests are recorded, and known unverified items are disclosed.

## Phase 9 — Deployment preparation

- [ ] Verify that the intended branch is the deployment branch before pushing a release.
- [ ] Verify that all runtime dependencies are listed in requirements.txt.
- [ ] Validate the configured entry point and Streamlit configuration.
- [ ] Deploy first to a staging copy or a private test deployment.
- [ ] Smoke-test the deployed app for cold-start success, charts, sliders, optimization and progress behavior.
- [ ] Review logs and resource usage after deployment.
- [ ] Promote to public production only after numerical and UI verification.
- [ ] Record deployment URL, commit SHA, date, rollback method and known limitations in memory.md.

**Exit criteria:** The live app matches the verified source commit, startup succeeds, and its educational/engineering limitations are visible.

## Current checkpoint

Completed code and automated regression/CI work is documented in memory.md. Browser/device verification, independent engineering review, durability of student records, added stability diagnostics and deployment remain follow-up work unless memory.md has a newer evidence-backed update.
