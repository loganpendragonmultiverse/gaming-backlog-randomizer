# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI also audits dependencies and runs the supported OS/Python matrix.

## 1.1.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Repair the two-game example and add eligibility previews, CSV input, decision history, cooldowns and pool comparisons.

## 1.1.1 acceptance

Reject non-finite hard duration limits before making a draw.

Verify Reject NaN and infinite max_hours values with actionable errors; Retain finite hard-limit filtering and source/output protections. Run the full existing quality and build gates; release only through protected PR checks and verified tag artifacts.

## 1.2.0 acceptance

Keep a seeded draw consistent when the same backlog is reordered.

Verify Add opt-in --stable-ids sorting before weighted draws and previews; Record a SHA-256 identity for effective selection inputs and mode in reports/history; Preserve the original input-order mode and reject blank or duplicate IDs in stable mode. Run the full existing quality and build gates; release only through protected PR checks and verified tag artifacts.

## 1.2.1 acceptance

Recover cleanly when writing a report and its companion file fails.

Verify Stage every file before reserving new output names and never overwrite existing destinations; Roll back only unchanged files created by the failed command, preserving concurrent changes; Keep stdout delivery inside the output operation and test permission failures, collisions and retry. Run the full existing quality and build gates; release only through protected PR checks and verified tag artifacts.

## 1.2.2 bounded numeric/date/identity fixes

Reject a non-finite eligible total before either preview or draw; retain existing ordinary weighted selection and seed behavior. Require canonical YYYY-MM-DD as_of and parsed cooldown history dates. Exclude ignored rule fields from stable effective-input identity. Regress finite-total overflow, ordinary/single-large weights, cross-runtime noncanonical dates and ignored metadata without changing source inputs or output recovery.
