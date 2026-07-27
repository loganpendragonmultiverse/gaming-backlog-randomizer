import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from gaming_backlog_randomizer.cli import main
from gaming_backlog_randomizer.core import choose, load_backlog, render_markdown


def backlog() -> dict[str, Any]:
    return {
        "version": 1,
        "games": [
            {
                "id": "north",
                "title": "North Road",
                "platform": "PC",
                "genres": ["adventure"],
                "moods": ["story"],
                "hours": 12,
                "owned": True,
                "weight": 2,
            },
            {
                "id": "grid",
                "title": "Quiet Grid",
                "platform": "Console",
                "genres": ["puzzle"],
                "moods": ["relaxed"],
                "hours": 5,
                "owned": False,
            },
        ],
        "rules": {
            "platforms": ["PC"],
            "genres": ["adventure"],
            "moods": ["story"],
            "max_hours": 20,
            "owned_only": True,
            "exclude_ids": [],
            "recent_ids": [],
        },
    }


def write(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_reproducible_selection_and_reasons() -> None:
    first = choose(backlog(), "same")
    second = choose(backlog(), "same")
    assert first["selected"] == second["selected"]
    assert first["selected"][0]["id"] == "north"
    assert first["excluded"][0]["reasons"] == ["platform", "genre", "mood", "not owned"]
    assert "Quiet Grid" in render_markdown(first)
    with pytest.raises(ValueError, match="positive"):
        choose(backlog(), "seed", 0)
    with pytest.raises(ValueError, match="only 1"):
        choose(backlog(), "seed", 2)


def test_all_rule_reasons() -> None:
    data = backlog()
    data["rules"] = {"max_hours": 6, "exclude_ids": ["north"], "recent_ids": ["north"]}
    report = choose(data, "seed")
    assert report["selected"][0]["id"] == "grid"
    assert report["excluded"][0]["reasons"] == ["length", "excluded id", "recently played"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda data: data.update(version=2), "version 1"),
        (lambda data: data.update(games=[]), "non-empty"),
        (lambda data: data.update(rules="bad"), "rules must"),
        (lambda data: data["games"].append(data["games"][0].copy()), "duplicate"),
        (lambda data: data["games"][0].update(genres="bad"), "list of text"),
        (lambda data: data["games"][0].update(hours=-1), "non-negative"),
        (lambda data: data["games"][0].update(weight=0), "positive"),
        (lambda data: data["games"][0].update(owned="yes"), "boolean"),
        (lambda data: data["rules"].update(platforms="PC"), "list of text"),
        (lambda data: data["rules"].update(max_hours=-1), "non-negative"),
        (lambda data: data["rules"].update(owned_only="yes"), "boolean"),
    ],
)
def test_validation(tmp_path: Path, change: Callable[[dict[str, Any]], None], message: str) -> None:
    data = backlog()
    change(data)
    path = tmp_path / "backlog.json"
    write(path, data)
    with pytest.raises((TypeError, ValueError), match=message):
        load_backlog(path)


def test_cli_json_and_safe_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "backlog.json"
    write(path, backlog())
    assert main([str(path), "--seed", "demo", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["eligible_count"] == 1
    output = tmp_path / "draw.md"
    assert main([str(path), "--seed", "demo", "--output", str(output)]) == 0
    assert main([str(path), "--seed", "demo", "--output", str(output)]) == 2
