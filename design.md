# Design — Truss Learning UI/UX

## 1. Design goals

1. Make the core learning flow usable on a 360px-wide phone, tablet, laptop, and desktop.
2. Explain structural concepts before asking students to manipulate parameters.
3. Show units, sign conventions, constraints, and model assumptions close to each result.
4. Use diagrams and direct feedback rather than dense prose alone.
5. Keep the interface calm and readable: avoid clutter, excessive color, horizontal clipping, and oversized metric cards.
6. Ensure color is never the only way information is conveyed; pair color with text, line patterns, labels, or table columns.

## 2. Page hierarchy

### Global shell

- Page title: **Truss Learning**.
- Sidebar navigation: Home, Learn, Solve, Stiffness Method, Challenge, Achievements, Reference.
- XP, progress, and achievement summaries stay in the sidebar but must not dominate narrow screens.
- Set Streamlit page configuration with layout="wide" and an automatic or collapsed sidebar strategy suitable for narrow viewports.
- Keep the CSS global, minimal, and scoped under the main application container so it does not unexpectedly style the sidebar or unrelated elements.

### Home

Use concise introductory text and a small set of primary entry points. Metrics may sit side by side on desktop but must wrap or stack on narrow viewports. Avoid text labels so wide that the mobile metric row overflows. The Home page should lead students to Learn or the interactive solver.

### Learn

- Show the selected tutorial title and ordinal position.
- Use a selectbox rather than a long horizontal radio list for tutorial navigation; six or more topic labels do not fit comfortably on mobile.
- Put the explanatory content before or adjacent to the diagram depending on the teaching sequence.
- Keep a clear previous/next path and a single “Mark as read” action.
- Embed the optimization lab within the determinacy-and-optimization tutorial.
- Marking the tutorial as read should award XP once, not again on repeated visits.

### Solve and Stiffness Method

- Display the structural diagram before the active prompt when possible.
- Keep the active step obvious; use expanders for completed or locked details.
- Inputs need visible units and tolerance-aware answer checking.
- Make result and error states distinct: correct, incorrect, not yet attempted, invalid input, and solver failure.
- Never require side-by-side reading of a diagram and equation on a phone. The mobile layout should make the order diagram → explanation → input → result natural.

### Challenge / Quiz

- One question at a time, one option per full-width touch target.
- Show the topic, progress, score, streak, selected answer, and explanation without tiny text.
- The correct answer should remain visible after submission.
- Do not silently reset a partially completed quiz.
- Keep keyboard navigation and readable focus states.

### Learn / Interactive tutorials

- Use a topic selectbox so all tutorial titles remain usable on mobile.
- On desktop, place theory/formulas in the left column and a Plotly diagram in the right column. On mobile, stack theory first and visualization second.
- Topic 1 must be a simple triangular roof truss with hoverable joints showing coordinates and hoverable members showing structural names.
- Use Plotly, not static PNGs, for lesson diagrams where interactive inspection adds value. Use one figure per topic with the same compact margins and readable hover typography.
- Put the topic heading, completion state, and XP reward before the split layout.
- Render formulas via st.latex in separate formula cards, particularly m + r = 2j and i = m + r − 2j.
- Keep previous, Mark as read, and next controls at the bottom. A completed topic has a disabled completion button.
- Preserve the existing optimization activity by injecting its renderer into the sixth tutorial rather than coupling learn.py directly to optimization_lab imports.
- Keep completion callbacks owned by main.py, so learn.py cannot accidentally double-award XP or bypass persistence.

### Optimization lab

Present this in a teaching sequence:

1. **Concept** — static determinacy count and a concise stability caveat.
2. **Controls** — load, allowable stress, displacement limit, and sensitivity mode in an expander.
3. **What-if experiment** — change CD area or Young's modulus.
4. **Force map** — let the student inspect the determinate or redundant solution.
5. **Optimization result** — show feasibility before interpreting volume differences.
6. **Deformation overlay** — optional toggle and scale.
7. **Member report** — dimensions, force, stress, utilization and status.
8. **Formula cards** — expandable equations and modeling assumptions.

Avoid forcing every control into the first viewport. Put secondary or frequently adjusted parameters into expanders, while keeping the important “Show Deflected Shape” toggle visible near the chart controls.

## 3. Responsive layout rules

### CSS breakpoints

The app uses a mobile breakpoint at 768px. On narrow screens:

- Reduce main content padding.
- Stack the children of horizontal column blocks to a single column.
- Allow long text, radio labels, and metric values to wrap.
- Make dataframes scroll horizontally rather than clipping the app viewport.
- Keep buttons and common form controls around 42–48 CSS pixels in height where practical.
- Keep tabs scrollable rather than squeezing each tab to illegible width.
- Ensure charts and images use their available container width.

The current implementation injects CSS with st.markdown(..., unsafe_allow_html=True). Streamlit's internal DOM selectors are not a permanent API: keep the CSS selectors narrow, review them after Streamlit upgrades, and validate actual device layouts. Prefer Streamlit native layout behavior first; CSS should refine it, not be the only source of responsive behavior.

### Desktop behavior

- Use two columns for comparisons only when each column retains readable labels and charts.
- Keep the member table full-width within its parent column.
- Use balanced whitespace, consistent card headings, and shared vertical rhythm.
- Use concise units and labels; avoid forcing long descriptions into cards.
- Use a maximum readable content width if the page looks too stretched on ultra-wide screens.

### Responsive CSS block

The block in main.py is the app-wide baseline. If future components need a distinct layout, add a class or a narrowly scoped wrapper and style only that component. Avoid global rules such as all div elements or all buttons without a container scope.

    @media (max-width: 768px) {
      .main .block-container {
        padding: 1rem 0.75rem 2rem !important;
        max-width: 100% !important;
      }

      .main [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        align-items: stretch !important;
        gap: 0.75rem !important;
        width: 100% !important;
      }

      .main [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
      }

      .main [data-testid="stMetricValue"] {
        font-size: clamp(1.2rem, 6vw, 1.8rem) !important;
        overflow-wrap: anywhere !important;
      }

      .main [data-testid="stDataFrame"] {
        max-width: 100% !important;
        overflow-x: auto !important;
      }

      .main [data-testid="stTabs"] [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        max-width: 100% !important;
      }
    }

This snippet is a design reference. Keep the authoritative, current version in main.py and ensure it remains synchronized with the app's real markup.

## 4. Plotly and Matplotlib guidelines

### Plotly (interactive analysis and optimization plots)

- Call st.plotly_chart(fig, use_container_width=True, config={"responsive": True, ...}).
- Use responsive chart width and compact margins: l=20, r=20, t=30–45, b=20, adjusted for titles and axes.
- Prefer scale-anchored geometry axes so the physical proportions of the truss are not visually distorted.
- Use a mobile-readable font size (normally 11–13px for labels; do not assume a fixed viewport).
- Keep hover details useful: member ID, length, area, force, stress, utilization and force type.
- Use hover templates for detail instead of permanently printing every numeric value on top of a dense truss.
- Avoid legends that take most of a phone's width. Explain colors in a short caption or compact legend.
- Only show the deformed mesh when requested, and clearly label the exaggeration factor.
- In plots with a deformed overlay, render the undeformed mesh as faint dashed gray and the deflected structure in solid force-mapped colors.
- Make the viewport tall enough to remain interactive on touch devices, but avoid excessive vertical plot height.
- If Plotly rendering is slow, inspect figure trace count and avoid duplicate traces or repeated recalculations.

### Member color and line-width semantics

Current design convention:
- **Blue:** tension.
- **Red:** compression.
- **Light gray:** zero-force member.
- **Dashed light gray:** undeformed reference mesh.
- **Solid, force-colored lines:** current or deflected structural geometry.

Line thickness represents normalized absolute axial force, capped to a readable maximum. An overstressed member may receive additional emphasis, but the utilization table remains the authoritative place for the threshold warning. Do not imply line width is utilization unless its scaling actually uses utilization.

Because red/blue semantics alone are not accessible to every user, include force type in hover text and in the member table. Use stable, high-contrast colors and do not rely on color-only warnings.

### Matplotlib

- Use tight layout, adequate figure dimensions, and legible labels.
- Display with st.pyplot(fig, use_container_width=True).
- Call plt.close(fig) after display to prevent figure accumulation.
- Avoid diagrams whose labels or notes are anchored outside the axes and get clipped on mobile.
- Static tutorial diagrams should remain understandable even when scaled down.

## 5. Input and control behavior

- Use st.slider for bounded continuous or discrete what-if values.
- Use st.select_slider when the user should pick from a small curated set of allowable values.
- Keep groups of secondary controls inside an expander titled by purpose, not generic “settings.”
- Use st.toggle for optional deformation rendering.
- For the CD sensitivity experiment, use a radio or segmented control for “Cross-sectional area A” versus “Young's modulus E.”
- Display EA/L in consistent units next to the active setting.
- Use unique keys for repeated controls, and keep widget value ranges consistent across reruns.
- Avoid number inputs with no validation, no visible units, or unexplained defaults.
- Explain when changing E affects stiffness but not the stress allowable, density, or other material assumptions.

## 6. Metrics, tables, and results

Avoid wide custom HTML tables for the primary report. Prefer st.dataframe or st.table, since they integrate with Streamlit and adapt to available width.

The member report must contain:
- Member ID
- Length L (m)
- Cross-sectional area A (mm²)
- Internal axial force P (kN)
- Axial stress σ (MPa)
- Utilization |σ| / σ_allow
- Force type / status

Use a soft-red row background and a clear message if utilization is greater than 1.0. Show utilization to three decimals and avoid rounding before the threshold test. If the optimizer fails or is infeasible, show that state before displaying any comparison claim. A lower volume is meaningful only among feasible solutions under the same inputs and constraints.

## 7. Pedagogical visual design

Every interactive activity should answer four questions:

1. **What am I changing?** Label the input and its units.
2. **What should I notice?** Give a short prediction or guiding question before the result.
3. **What happened?** Show force, stress, displacement, stiffness or volume in a visible comparison.
4. **Why did it happen?** Provide a concise engineering explanation and expandable equations.

For the determinacy lesson, explicitly teach:
- i = m + r − 2j is a counting check, not a proof of stability.
- In an ideal determinate truss with fixed geometry/loading, equilibrium fixes member forces; area affects stress and displacement, not the equilibrium force distribution.
- In a redundant truss, compatibility and stiffness (EA/L) can redistribute member forces.
- Adding a member adds material and an alternative load path; the optimized volume may rise or fall depending on geometry and limits.
- Every optimization result is conditional on the model, bounds and constraints.

Use worked examples, prediction prompts, and small, interpretable parameter changes. Avoid gamification that rewards a student for a numerically “good” answer without explaining the underlying mechanics.

## 8. Visual acceptance checklist

- [ ] Home page fits at 360px, 768px, 1024px and 1440px widths.
- [ ] Sidebar can be opened/closed on mobile and does not consume the content width persistently.
- [ ] All six tutorial topics can be selected on a phone.
- [ ] No horizontal page overflow in Learn, Solve, DSM, Quiz or optimization lab.
- [ ] Chart axes, labels, toggles and sliders are legible and usable with touch.
- [ ] Tables may scroll horizontally inside their own viewport but do not widen the whole page.
- [ ] Tension, compression, zero-force, overstress, solver error and infeasible optimization states are clearly distinguishable.
- [ ] Screen-reader text, keyboard navigation and focus behavior are not broken by CSS.
- [ ] Compare charts at identical scale and under identical loads when a visual comparison is intended.
