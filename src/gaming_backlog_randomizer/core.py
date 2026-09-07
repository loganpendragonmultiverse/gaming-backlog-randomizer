from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from datetime import date
from pathlib import Path
from typing import Any


def load_backlog(path: Path) -> dict[str, Any]:
    data: dict[str, Any]
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as source:
            csv_games: list[dict[str, Any]] = [dict(row) for row in csv.DictReader(source)]
        for game in csv_games:
            for field in ("genres", "moods"):
                game[field] = [
                    value.strip() for value in game.get(field, "").split("|") if value.strip()
                ]
            for field in ("hours", "weight"):
                if game.get(field):
                    game[field] = float(game[field])
                else:
                    game.pop(field, None)
            if "owned" in game:
                if game["owned"].lower() not in {"true", "false"}:
                    raise ValueError("CSV owned must be true or false")
                game["owned"] = game["owned"].lower() == "true"
        data = {"version": 1, "games": csv_games}
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("backlog must be a version 1 object")
    games = data.get("games")
    rules = data.get("rules", {})
    if not isinstance(games, list) or not games:
        raise TypeError("games must be a non-empty list")
    if not isinstance(rules, dict):
        raise TypeError("rules must be an object")
    seen: set[str] = set()
    for game in games:
        if (
            not isinstance(game, dict)
            or not isinstance(game.get("id"), str)
            or not isinstance(game.get("title"), str)
            or not isinstance(game.get("platform"), str)
        ):
            raise TypeError("each game requires string id, title, and platform")
        if game["id"] in seen:
            raise ValueError(f"duplicate game id: {game['id']}")
        seen.add(game["id"])
        for field in ("genres", "moods"):
            value = game.get(field, [])
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise TypeError(f"game {game['id']} field {field} must be a list of text")
        hours = game.get("hours")
        weight = game.get("weight", 1)
        if hours is not None and (
            not isinstance(hours, (int, float))
            or isinstance(hours, bool)
            or not math.isfinite(hours)
            or hours < 0
        ):
            raise ValueError(f"game {game['id']} hours must be non-negative")
        if (
            not isinstance(weight, (int, float))
            or isinstance(weight, bool)
            or not math.isfinite(weight)
            or weight <= 0
        ):
            raise ValueError(f"game {game['id']} weight must be positive")
        if "owned" in game and not isinstance(game["owned"], bool):
            raise TypeError(f"game {game['id']} owned must be boolean")
    for field in ("platforms", "genres", "moods", "exclude_ids", "recent_ids"):
        value = rules.get(field, [])
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise TypeError(f"rule {field} must be a list of text")
    max_hours = rules.get("max_hours")
    if max_hours is not None and (
        not isinstance(max_hours, (int, float)) or isinstance(max_hours, bool) or max_hours < 0
    ):
        raise ValueError("max_hours must be non-negative")
    if "owned_only" in rules and not isinstance(rules["owned_only"], bool):
        raise TypeError("owned_only must be boolean")
    return data


def _reasons(game: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    reasons = []
    if rules.get("platforms") and game["platform"] not in rules["platforms"]:
        reasons.append("platform")
    if rules.get("genres") and not set(game.get("genres", [])) & set(rules["genres"]):
        reasons.append("genre")
    if rules.get("moods") and not set(game.get("moods", [])) & set(rules["moods"]):
        reasons.append("mood")
    if rules.get("max_hours") is not None and (
        game.get("hours") is None or game["hours"] > rules["max_hours"]
    ):
        reasons.append("length")
    if rules.get("owned_only") and not game.get("owned", False):
        reasons.append("not owned")
    if game["id"] in rules.get("exclude_ids", []):
        reasons.append("excluded id")
    if game["id"] in rules.get("recent_ids", []):
        reasons.append("recently played")
    return reasons


def choose(
    data: dict[str, Any], seed: str, count: int = 1, *, preview: bool = False
) -> dict[str, Any]:
    if count < 1:
        raise ValueError("count must be positive")
    rules = dict(data.get("rules", {}))
    cooldown = data.get("cooldown_days", 0)
    if not isinstance(cooldown, int) or isinstance(cooldown, bool) or cooldown < 0:
        raise ValueError("cooldown_days must be a nonnegative integer")
    if cooldown:
        if not isinstance(data.get("as_of"), str):
            raise ValueError("cooldown requires an explicit as_of date")
        today = date.fromisoformat(data["as_of"])
        history = data.get("history", [])
        if not isinstance(history, list):
            raise ValueError("history must be an array of id/date decisions")
        recent = set(rules.get("recent_ids", []))
        for entry in history:
            if (
                not isinstance(entry, dict)
                or not isinstance(entry.get("id"), str)
                or not isinstance(entry.get("date"), str)
            ):
                raise TypeError("history entries require id and date strings")
            days = (today - date.fromisoformat(entry["date"])).days
            if days < 0:
                raise ValueError("history contains a future decision relative to as_of")
            if days < cooldown:
                recent.add(entry["id"])
        rules["recent_ids"] = sorted(recent)
    eligible = []
    excluded = []
    for game in data["games"]:
        reasons = _reasons(game, rules)
        if reasons:
            excluded.append({"id": game["id"], "title": game["title"], "reasons": reasons})
        else:
            eligible.append(game.copy())
    if count > len(eligible) and not preview:
        raise ValueError(f"requested {count} games but only {len(eligible)} are eligible")
    seed_number = int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8], "big")
    rng = random.Random(seed_number)
    pool = eligible.copy()
    selected = []
    for _ in range(0 if preview else count):
        pick = rng.choices(pool, weights=[float(game.get("weight", 1)) for game in pool], k=1)[0]
        selected.append(pick)
        pool.remove(pick)
    return {
        "version": 1,
        "seed": seed,
        "requested_count": count,
        "eligible_count": len(eligible),
        "excluded_count": len(excluded),
        "selected": selected,
        "excluded": excluded,
        "eligible": [
            {
                **game,
                "first_draw_probability": float(game.get("weight", 1))
                / sum(float(item.get("weight", 1)) for item in eligible),
            }
            for game in eligible
        ],
        "preview_only": preview,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Gaming Backlog Draw",
        "",
        f"Seed: `{report['seed']}` · Eligible: **{report['eligible_count']}** · Excluded: **{report['excluded_count']}**",
        "",
        "## Selected",
        "",
    ]
    lines.extend(f"- **{game['title']}** ({game['platform']})" for game in report["selected"])
    lines.extend(["", "## Eligible pool (first-draw probabilities)", ""])
    lines.extend(
        f"- **{game['title']}**: {game['first_draw_probability']:.1%}"
        for game in report["eligible"]
    )
    if report.get("comparison"):
        lines.extend(["", "## Alternative eligibility preview", ""])
        comparison = report["comparison"]
        lines.extend(
            f"- **{game['title']}**: {game['first_draw_probability']:.1%}"
            for game in comparison["eligible"]
        )
        lines.extend(
            f"- Excluded **{game['title']}**: {', '.join(game['reasons'])}"
            for game in comparison["excluded"]
        )
    if report["excluded"]:
        lines.extend(["", "## Excluded", ""])
        lines.extend(
            f"- **{game['title']}** — {', '.join(game['reasons'])}" for game in report["excluded"]
        )
    return "\n".join(lines).rstrip() + "\n"
