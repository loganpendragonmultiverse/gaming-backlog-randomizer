# Changelog

## 1.3.1 - 2026-10-20

- Include handoff documentation and runnable examples in wheels and source distributions.

- Return controlled input errors for integers outside the finite float range instead of raising OverflowError.
- Validate individual numeric values before report calculations; preserve supported finite values and original input files.
- Apply the same numeric checks to direct preview/draw calls, including excluded games and max_hours.

## 1.3.0 - 2026-10-17

- Apply reusable JSON hard rules to CSV or JSON primary backlogs with --rules.
- Validate all supplied history entries before output, even when cooldown is off.
- Preserve valid extra history metadata and keep alternative comparison rules independent.


## 1.2.2

- Reject overflowing eligible total weights consistently in previews and draws.
- Validate canonical as-of/cooldown dates across supported Python versions.
- Exclude ignored rule metadata from stable effective-input identities.

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
