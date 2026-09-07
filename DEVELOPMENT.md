# Development

Use the Python package in src and the pytest regression suite. CI must pass before release.

## 1.1.0 improvement session

Repair the two-game example and add eligibility previews, CSV input, decision history, cooldowns and pool comparisons.

`--preview` explains eligibility and first-draw probabilities without choosing a game. CSV accepts pipe-separated genres/moods, true/false ownership, numeric hours and weights. Use `--history history.json --cooldown-days 7 --as-of 2026-09-07` for explicit dated cooldowns, and `--history-output new-history.json` to write a new decision log after a draw. Entries record decisions, not proof of play. `--compare alternative.json` shows how changed rules or weights affect the pool; it does not claim improved recommendations. Original files and existing outputs are protected.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.
