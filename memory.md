# Memory — AI Development Checkpoint

> Living document for the AI coding assistant. Update it after meaningful code changes, tests, reviews or deployments. Keep entries factual, concise and dated. Separate verified facts from hypotheses and outstanding checks.

## 1. Project identity

- **Project:** Truss Learning
- **Repository:** mdaipayan/truss_learning_app
- **Active development branch:** claude/debug-and-run-app-deYiO
- **Primary entry point:** main.py
- **Main optimization module:** optimization_lab.py
- **UI framework:** Streamlit
- **Engineering method:** 2D linear-elastic pin-jointed truss Direct Stiffness Method
- **Sizing algorithm:** SciPy SLSQP through scipy.optimize.minimize
- **Interactive plotting:** Plotly
- **Static diagrams:** Matplotlib
- **Current release state:** Development branch only. Do not infer that the default branch or public app has been updated.

## 2. Current context

The app teaches:
- Ideal 2D truss behavior and truss types.
- Method of Joints and Method of Sections.
- Static determinacy and geometric stability concepts.
- Direct Stiffness Method, displacement calculation and member-force recovery.
- A gamified tutorial/quiz experience with XP, streaks and achievements.
- An interactive determinacy-and-optimization lab comparing a five-member determinate-by-count truss with the same layout plus member CD.

### Current source topology

- Nodes A, B, C, D.
- A is pinned; B is a vertical roller.
- Base members: AB, AC, BC, AD, BD.
- Added redundant member: CD.
- Vertical loads are applied at joints C and D.
- Diagonals AD and BC cross without a connected joint at their geometric intersection.
- Five-member topology has m = 5, r = 3, j = 4 and i = m + r − 2j = 0.
- Six-member topology has m = 6, r = 3, j = 4 and i = 1.
- The count is a determinacy check, not a proof of geometric stability.

### Key file responsibilities

- main.py: page configuration, global CSS, navigation, tutorial rendering, app pages.
- questions.py: tutorial content and quiz question bank.
- game.py: progress, XP, levels, achievements, progress load/save.
- diagrams.py: static Matplotlib diagrams.
- solver.py: interactive Method of Joints worked steps.
- dsm_solver.py: small example of direct stiffness analysis and display helpers.
- optimization_lab.py: DSM, optimization objective/constraints, force recovery, sensitivity lab, Plotly plots and member tables.
- requirements.txt: runtime dependencies.
- tests/test_optimization_lab.py: numerical and plot-helper regression tests.
- .github/workflows/python-checks.yml: dependency install, compileall and unittest CI.
- architecture.md, design.md, rules.md, task.md, production.md, memory.md: AI context documentation.

## 3. Implemented work (evidence-backed at this checkpoint)

### Determinacy/optimization lesson
- [x] Added the sixth tutorial, “Determinacy and Truss Optimization”.
- [x] Added four quiz questions on determinacy and optimization.
- [x] Added an illustrated determinate/indeterminate-by-count diagram.
- [x] Added a DSM analysis function for the four-joint truss.
- [x] Added continuous area sizing with stress and nodal-displacement constraints using SLSQP.
- [x] Added a what-if experiment to vary member CD's area A or Young's modulus E.
- [x] Added display of CD's axial stiffness EA/L.
- [x] Added a selector and live force-map plot for the current what-if setting.
- [x] Added force type mapping: blue for tension, red for compression, light gray for zero force.
- [x] Added member line-width scaling with absolute axial force.
- [x] Added optional deflected-shape overlay with dashed undeformed mesh and a 10x–100x exaggeration control.
- [x] Added member table with length, area, force, stress, utilization and force type.
- [x] Added soft-red table-row highlighting and explicit messaging when utilization exceeds 1.0.
- [x] Added formula cards for determinacy and sizing optimization.
- [x] Added a responsive Streamlit chart configuration and main-content CSS for narrow viewports.
- [x] Added Plotly to requirements.txt.

### Automated verification
- [x] Added unit tests covering the two counting indices.
- [x] Added a test that determinate forces remain invariant when only member areas change (same geometry and loads).
- [x] Added a test that varying CD's E changes redundant force sharing.
- [x] Added a test that equivalent CD EA/L produces equivalent force solutions.
- [x] Added a test for default optimization feasibility.
- [x] Added tests for plot traces and utilization reporting.
- [x] Added a GitHub Actions workflow.
- [x] GitHub Actions run 39085285180 completed successfully for commit dad593fc546ad8aa21673d3119f6bad8487c9ed3. It included Python compile and unittest steps. See: https://github.com/mdaipayan/truss_learning_app/actions/runs/39085285180

### AI context files
- [x] architecture.md
- [x] design.md
- [x] rules.md
- [x] task.md
- [x] production.md
- [x] memory.md

## 4. Important model assumptions and limitations

These are known limitations, not necessarily bugs:

1. **Educational model only.** It does not check buckling, connection capacity, fatigue, fabrication, load combinations, self-weight feedback or IS-code compliance.
2. **Linear-elastic small-displacement truss.** Members carry axial force only; no bending, geometric nonlinearity or material nonlinearity.
3. **Stability checks are incomplete.** The count i = m + r − 2j is only a first screen. A singular matrix is caught, but a comprehensive mechanism/rank/stability diagnostic is not yet implemented.
4. **Sizing material assumption.** The optimizer uses one baseline modulus for its area sizing. Changing E is part of the what-if sensitivity experiment; it is not yet a general multi-material sizing optimizer.
5. **Displacement constraint definition.** The current optimizer constrains the resultant in-plane displacement magnitude at every joint. A real project may require direction-specific serviceability limits.
6. **Continuous areas.** Optimization uses bounded continuous areas, not discrete market section sizes or fabrication/catalog constraints.
7. **No self-weight feedback.** Volume is minimized, but changing area does not add member self-weight to the applied load vector.
8. **Persistence is temporary.** game.py isolates progress by generated session key and temporary files. It does not implement authenticated student identities or durable database storage.
9. **Responsive CSS needs real-browser verification.** Streamlit DOM selectors may change between releases, and responsive CSS in source is not evidence of a visually correct phone layout.
10. **Deployment not confirmed.** Changes were committed to the working branch. Do not state that the production deployment was updated.

## 5. Known follow-up work / open issues

### High priority
- [ ] Visually test all primary pages at widths 360px, 390px, 768px, 1024px and 1440px.
- [ ] Confirm the sidebar behavior on phones; main.py currently sets initial_sidebar_state to expanded. Consider automatic/collapsed behavior if it improves actual mobile usability.
- [ ] Run CI on the latest documentation-only head and record its result; the last recorded successful code check is the run above.
- [ ] Independently hand-check one member-force/displacement solution and record the check.
- [ ] Add tests for singular/unstable geometry, invalid inputs and infeasible optimization limits.
- [ ] Review optimizer failure/retry selection and confirm infeasible candidates cannot be presented as feasible or optimal.
- [ ] Inspect the full current diff before merging or deploying.

### Medium priority
- [ ] Add explicit stiffness rank/stability diagnostics with student-friendly explanations.
- [ ] Add “predict before adjusting” and post-experiment reflection prompts.
- [ ] Improve governing-constraint reporting and area-bound reporting for optimization results.
- [ ] Review chart legibility on small/touch screens and ensure deformation scale is conspicuous.
- [ ] Decide whether durable identity-based student progress is a product requirement; if yes, design authentication and persistence before building it.
- [ ] Add optional code-compliant member checks only after defining code edition, load combinations, effective lengths, buckling model and independent validation.

### Release tasks
- [ ] Run the local test suite in a clean environment.
- [ ] Start Streamlit and smoke-test every navigation path.
- [ ] Complete manual mobile/tablet/desktop checks.
- [ ] Confirm deployment branch and hosting settings.
- [ ] Deploy only with explicit user authorization.
- [ ] Record deployed commit, URL, date and rollback plan if released.

## 6. Dependency baseline

Current requirements.txt declarations:

    streamlit>=1.35.0
    matplotlib>=3.8.0
    numpy>=1.24.0
    pandas>=2.0.0
    scipy>=1.10.0
    plotly>=5.20.0

These are lower bounds, not an exact lock. Verify the resolved package versions in the actual deployment environment.

## 7. AI collaboration rules

Before a new task:
1. Read this document and the relevant current source files.
2. Verify the active branch/head and any recent commits.
3. Turn the request into a small checklist in task.md if it spans multiple files or phases.
4. Identify calculations, UI behavior, educational content, tests and documentation affected.
5. Implement a bounded patch on the working branch.
6. Review the resulting file content and numerical units/sign conventions.
7. Run compile checks, tests and CI; record the exact successful commit SHA.
8. Mark items in this file only after evidence exists.
9. State what was not tested. Do not claim a browser test, engineering validation or deployment that did not occur.
10. Do not merge or deploy without explicit authorization.

## 8. Change log

### 2026-10-18 — Context files baseline
- Added architecture, design, rules, task, production and memory documentation to guide future coding-assistant work.
- Captured existing modules, model assumptions, numerical contracts, responsive design goals, current automated test coverage, known limitations and outstanding verification.
- No production deployment performed as part of creating these documentation files.

### 2026-10-18 — Responsive optimization lab refactor
- Added Plotly-based member force and deformation visualization.
- Added area/modulus sensitivity for redundant member CD.
- Added per-member stress and utilization reporting with overstress styling.
- Added mobile CSS adjustments, regression tests and GitHub Actions.
- GitHub Actions run 39085285180 passed compile and unittest checks at commit dad593fc546ad8aa21673d3119f6bad8487c9ed3.
- Browser/device testing and production deployment remain unverified.

## 9. How to append the next checkpoint

Append a dated entry with:
- Goal and files changed.
- Commit SHA(s).
- Tests run and their actual results.
- Manual validation (device/browser and viewport sizes).
- CI run URL and exact head SHA.
- Remaining risks, known regressions and rollback reference.
- Deployment status, only if deployment was actually performed.
