# Rules — AI Coding Assistant Contract

These rules are mandatory for all changes in Truss Learning. Prefer small, testable, reversible changes over broad rewrites.

## 1. Golden rules

1. Read the current code before proposing or editing it. Do not assume this document is newer than the implementation.
2. Keep the app modular. Do not duplicate the DSM, force recovery, optimization objective, constraint checks, or progress rules across UI functions.
3. Preserve working features unless the task explicitly calls for changing them.
4. Never claim a change passed runtime tests merely because the code was committed or compiles.
5. Do not deploy automatically. Make changes on the requested working branch, inspect the diff, run checks, and report deployment status explicitly.
6. Structural calculations must remain transparent, unit-aware, testable, and clearly labeled as educational unless proper design-code verification has been implemented.
7. Do not invent project files, API functions, solver fields, or external services. Inspect the repository before relying on a name or signature.

## 2. Python style and typing

- Target the Python version configured in CI. Prefer broadly supported Python 3.11 syntax unless the project intentionally raises its minimum version.
- Use four spaces, descriptive snake_case identifiers, and meaningful constants for engineering thresholds.
- Add type annotations to public and reusable functions. Use concrete input and return types where practical.
- Use dataclasses or TypedDict only if they reduce ambiguity without making a small educational module unnecessarily complex.
- Give public functions a docstring explaining purpose, units, sign conventions, and important assumptions.
- Avoid one-letter variables outside standard formulas and compact matrix operations. In teaching calculations, explain conventional variables (E, A, L, P, σ, δ).
- Do not use mutable default arguments. Create defaults inside the function.
- Avoid module-level mutable application state. Use immutable constants for geometry and fixed topology.
- Break long functions into pure calculation helpers and small UI renderers when doing so improves testability.
- Prefer f-strings, explicit names, and small readable expressions to opaque abstractions.
- Do not suppress warnings broadly, catch bare Exception without a reason, or silently convert failures to zeros.
- Do not add unused dependencies, unused imports, or speculative abstractions.
- Keep comments focused on why a choice exists, especially units, stability assumptions, sign conventions and numerical tolerances.

## 3. Engineering calculation contracts

### Units

Document units at the API boundary. Current optimization-lab convention:
- Coordinates and lengths: metres.
- Young's modulus: GPa.
- Cross-sectional area: mm².
- Nodal loads and member forces: kN.
- Displacements returned for reporting: mm.
- Axial stress: MPa.
- Volume: litres when computed as Σ(L in m × A in mm²) / 1000.

Under this convention, the numerical value E_GPa × A_mm2 / L_m is the axial stiffness in kN/m. If units are changed, update the derivation, every relevant calculation, displayed captions, and tests together.

### Sign convention

- Positive axial member force means tension.
- Negative axial member force means compression.
- Stress follows the same sign as axial force for positive area.
- Utilization is absolute stress divided by the chosen allowable stress; it must be nonnegative.
- A zero-force label must use a documented numerical tolerance. Do not use exact floating-point equality.

### Determinacy and stability

- Use i = m + r − 2j only as a determinacy-counting check.
- The displayed reaction count must refer to independent external reaction components, not merely support symbols.
- Never claim i = 0 proves geometric stability.
- Singular reduced stiffness matrices must generate an explicit stability/support/geometry diagnostic.
- If stability or rank is not checked programmatically, say so in the UI and documentation.
- A crossing of two lines is not a connected joint unless the topology explicitly defines a node there.

### DSM calculation rules

- Assemble each element stiffness matrix into the global K using an explicit degree-of-freedom map.
- Apply boundary conditions to the correct DOF indices.
- Solve only the free-DOF system; do not invert K explicitly.
- Recover member force using projected relative displacement along the member axis.
- Validate lengths, area, Young's modulus, loads and geometry before analysis.
- Avoid modifying the user's geometry or inputs silently to make a solver succeed.
- Report a singular matrix or invalid topology as an understandable UI state, not as a stack trace.

### Optimization rules

- The objective and each constraint must be independent, named functions or small closures with clear units.
- SciPy SLSQP inequality constraints must follow the convention margin >= 0.
- Always check both optimizer termination status and independently recomputed feasibility.
- Do not label a result “optimal” solely because minimize returned a result object.
- Do not compare volumes as winners unless both designs are feasible under the same load, stress limit, displacement limit, area bounds and assumptions.
- Preserve member area bounds and make them explicit to students.
- Do not generalize the educational optimizer as code-compliant sizing.
- If compression buckling is not checked, say so near the results.
- Do not silently use an infeasible result if an alternative optimizer start is tried. Select retry results only using explicit feasibility and objective criteria.

## 4. Streamlit best practices

### Application setup

- Call st.set_page_config once, before other Streamlit output.
- Keep the primary layout wide where useful, then make the content responsive.
- Keep CSS in a clear, documented block and scope selectors to the app content.
- Do not treat Streamlit's internal data-testid attributes as stable public APIs. After upgrading Streamlit, inspect the DOM and retest mobile layouts.

### Session state and widgets

- Use st.session_state only for session-specific UI or user progress that belongs to that session.
- Give each repeated or dynamically rendered widget a stable, unique key.
- Avoid using widget labels as a substitute for stable keys.
- Initialize defaults centrally or through small helpers before reading them.
- Never store a mutable user/session object in a global variable shared by all sessions.
- Do not use one global temporary save file for all students.
- Session-specific /tmp files isolate writes better than a shared file but are not durable persistence. Do not describe them as authenticated student records.
- Keep a quiz answer, current step, toggle, or slider value only as long as its behavior requires. Reset dependent state deliberately when the active model changes.
- Keep controls discoverable. Move secondary controls into meaningful expanders, but do not hide essential learning instructions.

### Caching

Use st.cache_data for deterministic computations with serializable outputs, such as the optimizer result for a fixed combination of load and constraint settings.

- Include every parameter that affects the output in the function arguments.
- Avoid reading mutable session state or hidden globals from a cached function.
- Do not cache random quiz shuffles as deterministic analysis.
- Do not cache file writes, user-specific secrets, or mutations.
- If model constants or topology can change during a session, pass them explicitly or version the cache key.
- Add a test to ensure a cached and uncached result are equivalent when practical.

Use st.cache_resource only for an expensive resource that should be shared (for example, a read-only model instance or database connection pool) and is safe for concurrent sessions. Do not use it for mutable per-student state.

### Rendering

- Use st.plotly_chart(..., use_container_width=True, config={"responsive": True, ...}) for responsive Plotly charts.
- Use st.pyplot(fig, use_container_width=True) for Matplotlib figures, and close figures after rendering.
- Use st.dataframe for rich tables; avoid wide custom HTML tables as the main result output.
- Keep UI rendering functions responsible for presentation and orchestration, not numerical model internals.
- Avoid repeated calls to the same expensive optimizer within one rerun. Cache fixed-input optimization results with all relevant inputs as keys.
- Provide context around metrics and tables; a naked number is not enough for teaching.

## 5. Error handling and student-facing messages

Expected invalid inputs should be handled at a clear boundary and converted to an actionable message.

Examples:
- Nonpositive or nonfinite area/modulus/load → explain which value must be positive and finite.
- Singular K matrix → suggest checking supports, connectivity, or geometric stability.
- Optimizer not converged → show that status and do not assert feasibility without checking constraints.
- Infeasible constraints → suggest which limit may need review and state that the current design did not pass.
- Save failure → inform the user that progress could not be stored without falsely claiming persistence.
- Plot failure → keep the page navigable and display a concise diagnostic.

For expected failures, use st.warning, st.error, or an explanatory status block. Log technical details for developers where useful, but do not expose secrets or overwhelming traces to students. Never use a success status for a failed or infeasible result.

## 6. Dependency management

- Add dependencies only when the implementation actually imports them.
- Update requirements.txt in the same change as the new import.
- Keep CI and local instructions consistent with the supported Python version.
- Use reasonable lower bounds for this educational app; pin a version only when compatibility or reproducibility justifies it.
- After changing Streamlit, Plotly, SciPy, NumPy or pandas, run the complete regression suite and inspect relevant APIs.
- Do not upgrade all dependencies in an unrelated code change.

## 7. Tests required for engineering changes

Minimum checks for the optimization lab:
- Determinacy counts for both topologies.
- Determinate member forces remain fixed when only areas change (same geometry and loads).
- A redundant member's relative axial stiffness can change force distribution.
- Equivalent EA/L cases produce equivalent linear-elastic force solutions within tolerance.
- Feasible optimization results satisfy all declared stress and displacement limits.
- Infeasible optimization results are flagged, not called optimal.
- Member force, stress and utilization calculations follow the documented unit convention.
- Plot helper has an undeformed trace and a deformed trace when the overlay is enabled.
- Member report shows the correct number of rows and utilization column.
- Tutorial navigation and quizzes include any newly added topics.
- A UI change should be manually verified at narrow and wide widths in a browser; compileall alone cannot prove visual responsiveness.

Use tolerances deliberately; do not make tests so loose that sign/unit bugs pass.

## 8. Git and review contract

For every implementation task:
1. Inspect the branch and current versions of the files to be changed.
2. Make a bounded patch on the intended branch.
3. Review the full changed-file content, not just a success response.
4. Run compile checks and numerical tests.
5. Check the GitHub Actions result where available.
6. Summarize files changed, tests actually performed, known limitations and deployment status.
7. Do not merge or deploy unless the user explicitly asks.
