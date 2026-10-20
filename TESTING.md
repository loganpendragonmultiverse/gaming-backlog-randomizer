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

## 1.3.0 history validation and reusable rules

Validate every supplied history entry before any output, with or without cooldown. Preserve valid extra metadata and source files. Test malformed shapes, missing fields, invalid calendar dates and noncanonical dates on preview and draw paths; a successful appended history must work in a later cooldown.

Add --rules for a primary CSV or JSON backlog. It replaces embedded rules; --compare retains the alternative file's own rules. Reuse the existing hard-rule validation and stable-input identity logic. Exercise preview, draw, history output, comparisons, invalid rules and unchanged input/rule files. Keep normal protected checks and independent exact-head review.

## 1.3.1 numeric boundaries

Reject actual JSON integers `10**400` and `-(10**400)` with actionable finite-number errors. Cover NaN/infinity, booleans, numeric strings, negative/zero boundaries, the maximum finite float and aggregate overflow. Verify CLI failures leave inputs unchanged and create no output or companion file. Keep the full quality, dependency audit, protected PR/main/tag and original installed wheel/source-distribution gates. Do not clamp values or alter ordinary seeded selection.
