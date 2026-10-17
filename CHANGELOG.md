# Changelog

## 1.2.1 - 2026-10-17

- Reject duplicate CSV columns and mismatched row widths before producing a draw or history file.

- Stage every file before reserving new output names and never overwrite existing destinations
- Roll back only unchanged files created by the failed command, preserving concurrent changes
- Keep stdout delivery inside the output operation and test permission failures, collisions and retry

## 1.2.0 - 2026-10-17

- Add opt-in --stable-ids sorting before weighted draws and previews
- Record a SHA-256 identity for effective selection inputs and mode in reports/history
- Preserve the original input-order mode and reject blank or duplicate IDs in stable mode

## 1.1.1 - 2026-10-17

- Reject NaN and infinite max_hours values with actionable errors
- Retain finite hard-limit filtering and source/output protections

## 1.1.0 - 2026-09-07

- Repair the two-game example and add eligibility previews, CSV input, decision history, cooldowns and pool comparisons.
- Added regression coverage for the audited behavior and invalid inputs.

## 1.0.0 - 2026-07-26

- Added explicit backlog filters and exclusion reasons.
- Added reproducible weighted selection without replacement.
- Added Markdown and JSON audit reports.
