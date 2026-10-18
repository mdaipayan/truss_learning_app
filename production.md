# Production — Deployment and Operations

## 1. Deployment philosophy

Treat production as a separate release step. A Git push is not proof that the deployed Streamlit app works. A successful Python CI workflow is necessary but cannot validate actual phone layouts, every Streamlit widget, browser behavior, or structural-design adequacy.

Recommended path:

1. Commit and review changes on the working branch.
2. Ensure GitHub Actions passes on the exact candidate commit.
3. Run local tests and a browser smoke test.
4. Promote the reviewed commit to the configured production branch.
5. Deploy to a test deployment or controlled release first where possible.
6. Confirm the deployed app's commit, logs, charts, controls and optimization results.
7. Record release metadata and rollback steps in memory.md.

Do not automatically merge or deploy unless the repository owner explicitly asks.

## 2. Streamlit Community Cloud deployment

Streamlit Community Cloud is a possible hosting target for this app. Confirm current platform limits and setup requirements in Streamlit's official documentation before a release; platform behavior and limits may change.

### Preparation

- Ensure all runtime Python modules, static files and configuration required by the app are committed.
- Ensure requirements.txt is in the repository root, with all required third-party packages listed.
- Keep main.py as the entry point unless the repository structure changes.
- Verify .streamlit/config.toml contains only intentional, non-secret settings.
- Do not commit .env files, API keys, credentials, student exports, private progress data or local caches.
- Confirm the deployed branch is the intended release branch. The working branch is not automatically the production source unless configured that way.
- Review the last successful CI run and confirm it matches the candidate source commit.

### Create or update the app

1. Push the reviewed source to GitHub.
2. Open Streamlit Community Cloud and authenticate with the authorized GitHub account.
3. Create an app (or open the existing app).
4. Select the repository, intended branch, and entry-point path main.py.
5. Add required secrets through the hosting platform's secrets/settings facility only if the app genuinely needs them. This application currently does not require a secret for its local numerical solver.
6. Deploy and wait for the platform to finish installation and startup.
7. Open the public/private test URL and run the smoke tests below.
8. Inspect platform logs after startup and after exercising the optimizer.
9. Record deployment time, URL, branch, commit SHA, and rollback version in memory.md.

### Deployment caveats

- The app's current game-progress implementation uses temporary files scoped by session key. Hosting restarts, multiple workers, reconnections or new sessions may lose progress; do not advertise durable progress until a database-backed persistence layer is implemented and tested.
- Files stored in an app container must not be treated as permanent storage.
- Do not change the default branch or public deployment settings as a side effect of ordinary feature development.
- If the deployment uses another host or internal platform, follow that platform's current official deployment instructions instead.

## 3. Dependency policy

Current runtime requirements:

    streamlit>=1.35.0
    matplotlib>=3.8.0
    numpy>=1.24.0
    pandas>=2.0.0
    scipy>=1.10.0
    plotly>=5.20.0

These lower bounds describe intended compatibility, not a guarantee that every future package release remains compatible. The exact resolved versions should be captured in a tested deployment environment.

Rules:
- Add every imported runtime dependency to requirements.txt.
- Do not add developer-only tools to production requirements unless the deployed app imports them at runtime.
- Avoid unbounded speculative upgrades. Update packages deliberately and run the full tests.
- For reproducible deployments, consider a tested lock file or a generated, platform-compatible exact-version requirements file after verifying the target Python and operating environment.
- Do not blindly pin machine-specific packages or include unnecessary platform-only packages.
- Test dependency changes in a clean environment before deployment.
- Record the Python version used by CI and the deployment platform.
- If a native wheel or a platform-specific SciPy/NumPy issue appears, use the hosting platform's supported Python version and package guidance rather than random downgrades.

## 4. Performance rules

### Numerical work

- Keep stiffness assembly, displacement solve, member-force recovery and optimization separated into small functions.
- Cache deterministic optimizer results with st.cache_data and all relevant input values as explicit arguments.
- Recompute results only when inputs that affect them change.
- Avoid running the same SLSQP optimization more than once during a single rerun for identical arguments.
- Avoid an optimizer call on every slider drag if that becomes expensive; consider a form or explicit “Run optimization” button after measuring latency.
- Do not cache session state, mutable user data, secrets or side-effecting save operations.
- Keep topology small in the current lesson, but establish profiling before increasing the model's size.
- Use a linear solve rather than explicitly inverting the global stiffness matrix.
- Fail fast on nonfinite inputs, zero-length members and singular reduced stiffness matrices.

### Plot and table rendering

- Create only the Plotly traces needed for the current view.
- Use responsive charts, concise margins, and readable hover details.
- Render the undeformed mesh only when the deformation overlay is on.
- Do not run analysis separately for each member trace.
- Keep static Matplotlib figures closed after display to prevent memory growth.
- Prefer a clear table over many individual Streamlit metrics when reporting all member values.
- Do not send unnecessary high-resolution images or large dataframes to the browser.
- Use cache keys that include load, stress limit, displacement limit, topology and any future material, area-bound or model parameters that affect the result.

### Streamlit behavior

- Streamlit reruns the script on widget changes. Keep initialization deterministic and avoid repeated mutation of progress data on simple reruns.
- Use stable, unique widget keys.
- Avoid rendering the same large component repeatedly in nested functions.
- Keep the sidebar and CSS compact. Mobile responsiveness must not require a costly resize listener or custom JavaScript.
- Use st.status or a concise spinner for optimization only if its runtime justifies it; avoid user-visible “loading” animation for near-instant operations.
- Treat Streamlit's internal CSS selectors as unstable and retest after upgrades.

## 5. Security and privacy

- Never commit API keys, access tokens, database passwords, service account JSON, student details, or private progress files.
- Store secrets in the host's secrets manager. Do not expose secrets in logs, UI, tracebacks or source code.
- If adding a database, use least-privilege credentials and enforce authorization at the server/data boundary.
- Do not assume a random session key is a student identity or an authentication mechanism.
- Avoid displaying one student's data in another session.
- Do not store personally identifiable student data without an explicit requirement, access policy, retention policy and institutional approval.
- If any external AI service is introduced, document what data is sent to it and obtain appropriate authorization before sending student work or personal data.

## 6. Minimum release smoke test

Run these tests against the exact deployed commit:

### Startup and navigation
- [ ] App starts with no import error.
- [ ] Home, Learn, Solve, Stiffness Method, Challenge, Achievements and Reference pages open.
- [ ] Each of the six tutorial topics can be selected.
- [ ] The sixth tutorial opens the optimization lab.

### Optimization lab
- [ ] Default setting produces stable analysis results.
- [ ] Determinacy counts are 0 for the five-member topology and +1 for the added-CD topology.
- [ ] Switching between area A and modulus E controls displays the right slider and units.
- [ ] The current force map changes when the redundant member's effective EA/L changes.
- [ ] The deformation toggle reveals the dashed undeformed mesh and solid displaced geometry.
- [ ] Changing the deformation scale visibly changes the drawn displacement exaggeration.
- [ ] Member table columns, signs, stress and utilization values are legible.
- [ ] Overstress is highlighted when the ratio exceeds 1.0.
- [ ] Failed or infeasible optimization is not shown as a successful optimum.
- [ ] Formula cards and assumption warnings are present.
- [ ] The browser remains responsive during optimization.

### Responsive checks
- [ ] 360px and 390px phone viewports: no page-level horizontal overflow.
- [ ] 768px tablet width: controls and charts remain readable.
- [ ] 1024px and 1440px: comparison layout uses available space appropriately.
- [ ] Touch targets, tab controls and chart interaction are usable on mobile.
- [ ] Data tables scroll internally instead of stretching the whole viewport.

### State and persistence
- [ ] Two separate sessions do not overwrite each other's progress.
- [ ] Progress behavior across reconnects/restarts matches documented guarantees.
- [ ] No credentials, personal data or unexpected files appear in logs.

## 7. Rollback

- Keep the last known-good commit SHA and deployment metadata in memory.md.
- For a failed release, redeploy the last verified commit/branch using the platform's supported rollback process.
- Do not repair a live incident by making unreviewed unrelated changes to the default branch.
- Capture the error, affected commit, relevant redacted logs, rollback result, and follow-up action in memory.md.
- A rollback is complete only after a smoke test confirms that the previous release serves the app correctly.

## 8. Production readiness statement

Do not label the app “production-ready structural design software.” It is an educational analysis and sizing tool until the model, code checks, load cases, stability/buckling verification, validation evidence, and intended engineering use have been independently reviewed and qualified.
