# Architecture — Truss Learning

## 1. Purpose and scope

Truss Learning is an educational Streamlit application for teaching 2D pin-jointed truss analysis, static determinacy, the Direct Stiffness Method (DSM), and sizing optimization. It combines guided lessons, worked analysis steps, quiz/game mechanics, and an interactive optimization laboratory.

The architecture is intentionally modular. The Streamlit layer collects inputs and presents results; calculation modules perform analysis; the question bank and game module own educational content and progress rules.

This is a learning environment, not a certified structural-design package. Its current optimization model does not check compression-member buckling, connection strength, fatigue, fabrication constraints, load combinations, self-weight feedback, or IS-code compliance. Never represent its output as safe for construction.

## 2. Technology stack

| Layer | Technology | Responsibility |
|---|---|---|
| UI and application flow | Python, Streamlit | Navigation, controls, session state, layouts, explanations, feedback |
| Interactive charts | Plotly | Responsive force mapping and deformed-shape visualization |
| Engineering diagrams | Matplotlib | Static tutorial and solver diagrams |
| Numerical arrays | NumPy | Coordinates, matrix assembly, linear algebra, force/stress calculations |
| Tables and reports | pandas | Member-force, stress, utilization, and optimization comparison tables |
| Optimization | SciPy optimize.minimize / SLSQP | Continuous cross-sectional-area sizing subject to constraints |
| Automated checks | unittest, compileall, GitHub Actions | Syntax checks and numerical regression tests |
| Deployment target | Streamlit Community Cloud (planned option) | Hosted Streamlit application |

## 3. Current module structure

The project uses top-level Python modules. Keep this layout unless there is a clear benefit to introducing packages.

    truss_learning_app/
    ├── .github/
    │   └── workflows/
    │       └── python-checks.yml
    ├── .streamlit/
    │   └── config.toml
    ├── tests/
    │   └── test_optimization_lab.py
    ├── main.py                 # Streamlit entry point, navigation, global UI
    ├── home.py                 # Reusable responsive Home dashboard
    ├── questions.py            # Tutorial text and quiz question bank
    ├── game.py                 # XP, achievements, quiz/tutorial progress
    ├── diagrams.py             # Matplotlib structural and educational diagrams
    ├── solver.py               # Interactive Method of Joints teaching steps
    ├── dsm_solver.py           # Small DSM example solver and display helpers
    ├── optimization_lab.py     # Optimization-specific DSM, plots, tables and UI
    ├── requirements.txt        # Python runtime dependencies
    ├── architecture.md
    ├── design.md
    ├── rules.md
    ├── task.md
    ├── production.md
    └── memory.md

### Module boundaries

- **main.py** owns Streamlit initialization, global responsive CSS, navigation, page-level composition, and connects live game state to the Home renderer. It calls optimization_lab.render_lab() from the sixth tutorial. It should orchestrate, not contain a second copy of the optimization mathematics.
- **home.py** renders the landing dashboard: hero, CTA buttons, live rank/XP/streak/achievement cards, and module-navigation cards. It accepts a progress mapping and a required navigation callback, so it does not import or depend on main.py's router.
- **questions.py** stores the TUTORIALS and QUESTIONS content. Avoid mixing solver algorithms or Streamlit callbacks into this content-only module.
- **game.py** defines the progress schema, XP/levels, achievement rules, and progress load/save functions. Existing per-session temporary files do not provide durable identity-based student records.
- **diagrams.py** creates Matplotlib teaching diagrams. Each function should return a Figure; callers display and then close it.
- **solver.py** supplies known step data and accepted answers for the guided method-of-joints exercise. It is not the same solver as the general 2D stiffness analysis.
- **dsm_solver.py** demonstrates assembly, supports, displacements, member forces, and reactions for a small symmetric truss.
- **optimization_lab.py** owns the four-joint educational model, global stiffness assembly, displacement solve, member-force recovery, area-sizing objective/constraints, Plotly charts, tabular reports, and the interactive lab.
- **tests/** contains numerical regression tests. Keep numerical tests independent from Streamlit browser interaction wherever possible.

## 4. Data flow

### 4.1 Learning and navigation

1. main.py configures Streamlit and CSS.
2. _init() initializes st.session_state.
3. main.py's page_home() maps game state and quiz state to a progress mapping, then calls home.render_home(progress=..., navigate=go, ...).
4. The Home module renders buttons; route requests are delegated to the callback rather than owning a second router.
5. Sidebar navigation selects a page key.
4. The Learn page selects a tutorial by index from TUTORIALS.
5. The tutorial's static figure comes from DIAG_FNS; the sixth tutorial additionally calls optimization_lab.render_lab().
6. Completing a tutorial or quiz updates game state, awards XP/achievements, and calls the save helper.

### 4.2 Optimization-lab flow

    User controls
      ├── load at C and D
      ├── allowable axial stress
      ├── maximum nodal displacement
      ├── CD area OR CD Young's modulus
      └── deformation toggle and scale
              |
              v
    optimization_lab.py UI
              |
              +---- solve_design(...)
              |       |
              |       v
              |   DSM assembly -> supports/DOFs -> K_ff d_f = F_f
              |       |
              |       v
              |   displacements -> member axial force -> stress
              |
              +---- optimize_design(...)
                      |
                      v
                  SLSQP minimizes V = sum(L_i A_i)
                  subject to axial stress and displacement limits
                      |
                      v
               result dictionary
                      |
              +-------+-----------+
              |       |           |
              v       v           v
           Plotly   pandas      metrics/insights
           force    report
           map      table

There is no separate API or front-end server. Streamlit reruns Python when a widget changes. Use unique widget keys and keep expensive work behind cached, deterministic functions.

## 5. DSM formulation in the optimization lab

Each planar truss joint has two translational degrees of freedom, u_i and v_i. A bar member has length L, direction cosines c = Δx/L and s = Δy/L, and axial stiffness EA/L.

For the member DOF ordering [u_i, v_i, u_j, v_j], its global-coordinate stiffness matrix is:

\[
\mathbf{k}_e=\frac{EA}{L}
\begin{bmatrix}
c^2&cs&-c^2&-cs\\
cs&s^2&-cs&-s^2\\
-c^2&-cs&c^2&cs\\
-cs&-s^2&cs&s^2
\end{bmatrix}
\]

Assemble the element matrices into global K, create the global load vector F, apply support conditions, and solve the free-DOF system:

\[
\mathbf K_{ff}\mathbf d_f=\mathbf F_f
\]

Recover each axial member force from the relative displacement projected along that member's axis. The sign convention is **positive = tension, negative = compression**. Stress is P/A; with P in kN and A in mm², multiply P/A by 1000 to obtain MPa.

Current demonstration topology:
- Nodes A, B, C, D, with A pinned and B restrained vertically by a roller.
- Five base members for the determinate-by-count topology: AB, AC, BC, AD, BD.
- Add CD to introduce one degree of static indeterminacy by the count.
- Vertical loads act at C and D.

The geometry has crossing diagonals AD and BC which pass one another without a joint at the crossing. Do not silently treat the crossing as a connected joint.

For the unit convention in optimization_lab.py, E is in GPa, A in mm², and L in metres; the numerical value E_GPa × A_mm² / L_m is the member axial stiffness in kN/m. Test units whenever this convention changes.

## 6. Static determinacy and stability

The counting index displayed by the lesson is:

\[
i=m+r-2j
\]

where m is the number of bars, r is the number of independent external reaction components, and j is the number of joints.

- i = 0: determinate **by count**, subject to a separate stability and independence check.
- i > 0: indeterminate **by count**, assuming the constraints and members are independent.
- i < 0: insufficient restraints/unknown equilibrium equations by count; often unstable.

The equation is a screening rule, not a proof of geometric stability. A future solver should add explicit stability/rank checks and useful user-facing messages for mechanisms, redundant constraints, and singular stiffness matrices.

## 7. Optimization contract

The current optimizer chooses continuous member areas A_i, bounded between 100 and 5,000 mm²:

\[
\min_{\mathbf A} V=\sum_i L_iA_i
\]

subject to:

\[
|\sigma_i|\le \sigma_{\mathrm{allow}},\qquad
\|\mathbf d_j\|\le \delta_{\mathrm{allow}}
\]

The implemented displacement limit is applied to the magnitude of each joint's in-plane displacement. SLSQP uses inequality constraints in the form margin >= 0. Always evaluate the returned design independently and distinguish optimizer success from true constraint feasibility.

Important current limitations:
- Linear elastic, small-displacement axial-bar analysis only.
- Single material for the sizing optimization; sensitivity experiment can vary E for member CD.
- No member buckling check; compression stress alone is not sufficient for real steel-member design.
- No IS-code load combinations, factors, connection checks, fatigue, self-weight iteration, or fabrication constraints.
- A common-material volume comparison does not prove cost optimality.
- No user/student database or cross-session durable progress store is currently provided.

## 8. State, caching, and persistence

- Use st.session_state for transient view state, not module-level mutable globals.
- Keep a unique key per widget, including controls repeated in columns/loops.
- Use @st.cache_data for deterministic results that depend only on arguments, such as optimizer results. Include every input affecting the result in the cache key.
- Do not cache mutable session objects, credentials, private student records, or incomplete state.
- The game.py progress implementation uses a generated session key and temporary-file storage to prevent sessions from writing to the same file; it is not a persistent student identity system. Do not promise progress survives reconnects, container restarts, or new sessions.
- If durable records are required, design an explicit persistence layer (database plus authenticated student identity) before implementing it.

## 9. Engineering and UI error paths

- Validate positive finite areas, moduli, lengths, loads, and limits before matrix assembly.
- Catch linear-algebra singularity and report a likely stability/support issue rather than showing a Python traceback to students.
- Display optimizer convergence and feasibility separately.
- Keep the last valid output available when a new input is invalid only if that behavior is explicit and clearly labeled.
- Never silently replace failed values with zero or label a non-converged design as optimal.
- Distinguish analysis results from sizing recommendations and clearly label educational assumptions.

## 10. Architecture acceptance criteria

- UI modules call well-defined calculation functions and do not duplicate the DSM formulation.
- Calculation functions return plain data structures suitable for tests.
- The optimization is deterministic for fixed inputs and can be tested without a browser.
- Responsive plots and tables work at desktop and narrow phone widths.
- A failed or infeasible optimizer run displays a useful explanation.
- Mathematical formulas, units, sign conventions, and assumptions are documented next to the interactive experiment.
