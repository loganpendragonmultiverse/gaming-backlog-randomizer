# Gaming Backlog Randomizer With Rules

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
