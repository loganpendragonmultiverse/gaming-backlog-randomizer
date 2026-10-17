# Development

Use the Python package in src and the pytest regression suite. CI must pass before release.

## 1.1.0 improvement session

Repair the two-game example and add eligibility previews, CSV input, decision history, cooldowns and pool comparisons.

`--preview` explains eligibility and first-draw probabilities without choosing a game. CSV accepts pipe-separated genres/moods, true/false ownership, numeric hours and weights. Use `--history history.json --cooldown-days 7 --as-of 2026-09-07` for explicit dated cooldowns, and `--history-output new-history.json` to write a new decision log after a draw. Entries record decisions, not proof of play. `--compare alternative.json` shows how changed rules or weights affect the pool; it does not claim improved recommendations. Original files and existing outputs are protected.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.

## 1.1.1 acceptance

Reject non-finite hard duration limits before making a draw.

max_hours must be a finite nonnegative number. Seeded draws are reproducible for the same input ordering, rule values, seed and runtime contract; this patch does not silently change the draw ordering algorithm.

## 1.2.0 acceptance

Keep a seeded draw consistent when the same backlog is reordered.

Use backlog-randomizer backlog.json --seed weekend --stable-ids --count 2 --format json. Keep IDs attached to the same games when editing or reordering. stable-id-v1 sorts IDs by Unicode code point before the existing Python weighted draw. The same seed, effective metadata/rules and supported runtime reproduce selections despite array reordering. Identity excludes titles and unused metadata; it is an audit aid, not proof of play or a cryptographic random draw. Changes to weights, eligibility or cooldown history may change results. The default input-order-v1 mode retains earlier behavior.

## 1.2.1 acceptance

Recover cleanly when writing a report and its companion file fails.

Report and ledger/decision/history files are prepared together. If an ordinary write fails, the command removes only unchanged files it created, so you can fix the destination and retry. Existing files, source inputs and files changed by another process are preserved. Outputs are UTF-8 with LF endings. This handles ordinary write failures; it does not promise a multi-file transaction through power loss or recall text already read from stdout.
