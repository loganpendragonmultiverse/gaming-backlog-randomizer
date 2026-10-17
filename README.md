# Gaming Backlog Randomizer With Rules

> ⭐ **Gold Star Project**
> I consider this project complete. Fixes, maintenance and good new ideas are still welcome.
> [About Gold Stars](https://www.loganpendragonforge.com/open-source/?gold=1)
>
> Choose a game from your backlog using your own rules and weights, with an optional stable-ID mode that keeps seeded draws consistent when you reorder the list.

## Current release 1.2.1

Recover cleanly when writing a report and its companion file fails.

Report and ledger/decision/history files are prepared together. If an ordinary write fails, the command removes only unchanged files it created, so you can fix the destination and retry. Existing files, source inputs and files changed by another process are preserved. Outputs are UTF-8 with LF endings. This handles ordinary write failures; it does not promise a multi-file transaction through power loss or recall text already read from stdout.

## Updates in 1.2.0

Keep a seeded draw consistent when the same backlog is reordered.

Use backlog-randomizer backlog.json --seed weekend --stable-ids --count 2 --format json. Keep IDs attached to the same games when editing or reordering. stable-id-v1 sorts IDs by Unicode code point before the existing Python weighted draw. The same seed, effective metadata/rules and supported runtime reproduce selections despite array reordering. Identity excludes titles and unused metadata; it is an audit aid, not proof of play or a cryptographic random draw. Changes to weights, eligibility or cooldown history may change results. The default input-order-v1 mode retains earlier behavior.

## Updates in 1.1.1

Reject non-finite hard duration limits before making a draw.

max_hours must be a finite nonnegative number. Seeded draws are reproducible for the same input ordering, rule values, seed and runtime contract; this patch does not silently change the draw ordering algorithm.

[![CI](https://github.com/loganpendragonmultiverse/gaming-backlog-randomizer/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/gaming-backlog-randomizer/actions/workflows/ci.yml)

Gaming Backlog Randomizer chooses from a supplied backlog only after applying explicit platform, genre, mood, length, ownership, recent-play, and ID exclusions. Weighted selection is reproducible from a seed, and every rejected game keeps its reasons.

## Three-minute start

```bash
python -m pip install .
backlog-randomizer examples/backlog.json --seed weekend-26
backlog-randomizer examples/backlog.json --seed weekend-26 --count 2 --format json
```

Games can carry multiple genres and moods plus a positive selection weight. Rules are optional and conjunctive: a game must satisfy every supplied hard rule before it enters the weighted draw.

The tool does not query storefronts, recommend purchases, infer mood, or guarantee enjoyment. Estimated hours and metadata are supplied by the user. A seed reproduces a draw only for identical input and rules. Requires Python 3.10 or newer.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Version 1.1.0: reviewed improvements

Repair the two-game example and add eligibility previews, CSV input, decision history, cooldowns and pool comparisons.

```bash
backlog-randomizer examples/backlog.json --seed weekend --preview --format json
```

`--preview` explains eligibility and first-draw probabilities without choosing a game. CSV accepts pipe-separated genres/moods, true/false ownership, numeric hours and weights. Use `--history history.json --cooldown-days 7 --as-of 2026-09-07` for explicit dated cooldowns, and `--history-output new-history.json` to write a new decision log after a draw. Entries record decisions, not proof of play. `--compare alternative.json` shows how changed rules or weights affect the pool; it does not claim improved recommendations. Original files and existing outputs are protected.
