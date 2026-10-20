import json
import math
import sys
from pathlib import Path
from typing import Any

import pytest

from gaming_backlog_randomizer.cli import main
from gaming_backlog_randomizer.core import choose, load_backlog


def backlog(field: str, value: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "version": 1,
        "games": [{"id": "a", "title": "Boundary", "platform": "PC", "hours": 1, "weight": 1}],
        "rules": {},
    }
    (data["rules"] if field == "max_hours" else data["games"][0])[field] = value
    return data


@pytest.mark.parametrize("field", ["hours", "weight", "max_hours"])
@pytest.mark.parametrize(
    "value",
    [
        10**400,
        -(10**400),
        int(sys.float_info.max) + 1,
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        "2",
        -1,
    ],
)
def test_extreme_values_rejected_before_selection(tmp_path: Path, field: str, value: Any) -> None:
    data = backlog(field, value)
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValueError, match=field + " must be finite"):
        load_backlog(path)
    for preview in [False, True]:
        for stable in [False, True]:
            with pytest.raises(ValueError, match=field + " must be finite"):
                choose(data, "boundary", preview=preview, stable_ids=stable)
    assert path.read_bytes() == before


@pytest.mark.parametrize("field", ["hours", "weight", "max_hours"])
@pytest.mark.parametrize("value", [1, 1.5, 10**300, sys.float_info.max, int(sys.float_info.max)])
def test_supported_finite_values_are_preserved(tmp_path: Path, field: str, value: float) -> None:
    data = backlog(field, value)
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    loaded = load_backlog(path)
    assert (loaded["rules"] if field == "max_hours" else loaded["games"][0])[field] == value
    for preview in [False, True]:
        report = choose(loaded, "boundary", preview=preview, stable_ids=True)
        assert report["eligible_count"] == 1
        assert report["eligible"][0]["first_draw_probability"] == 1


def test_zero_hours_supported_but_zero_weight_rejected(tmp_path: Path) -> None:
    for field in ["hours", "max_hours"]:
        data = backlog(field, 0)
        data["games"][0]["hours"] = 0
        assert choose(data, "zero")["eligible_count"] == 1
    path = tmp_path / "zero.json"
    data = backlog("weight", 0)
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="positive"):
        load_backlog(path)
    with pytest.raises(ValueError, match="positive"):
        choose(data, "zero", preview=True)


def test_aggregate_overflow_and_smallest_positive_weight() -> None:
    data = backlog("weight", sys.float_info.max)
    data["games"].append({**data["games"][0], "id": "b"})
    for preview in [False, True]:
        with pytest.raises(ValueError, match="eligible total weight must be finite"):
            choose(data, "overflow", preview=preview)
    tiny = choose(backlog("weight", math.ulp(0.0)), "tiny")
    assert tiny["eligible"][0]["first_draw_probability"] == 1


@pytest.mark.parametrize("field", ["hours", "weight", "max_hours"])
@pytest.mark.parametrize("preview", [False, True])
def test_cli_extreme_integer_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], field: str, preview: bool
) -> None:
    path = tmp_path / "input.json"
    path.write_text(json.dumps(backlog(field, 10**400)), encoding="utf-8")
    before = path.read_bytes()
    report = tmp_path / "report.json"
    history = tmp_path / "history.json"
    args = [
        str(path),
        "--seed",
        "boundary",
        "--format",
        "json",
        "--output",
        str(report),
        "--history-output",
        str(history),
        "--as-of",
        "2026-10-20",
    ]
    assert main(args + (["--preview"] if preview else [])) == 2
    captured = capsys.readouterr()
    assert field + " must be finite" in captured.err and "Traceback" not in captured.err
    assert captured.out == ""
    assert path.read_bytes() == before
    assert not report.exists() and not history.exists()


@pytest.mark.parametrize("field", ["hours", "weight"])
def test_csv_extreme_number_is_a_controlled_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], field: str
) -> None:
    path = tmp_path / "input.csv"
    path.write_text(
        "id,title,platform," + field + "\na,Boundary,PC," + str(10**400) + "\n", encoding="utf-8"
    )
    before = path.read_bytes()
    output = tmp_path / "report.json"
    assert main([str(path), "--seed", "csv", "--preview", "--output", str(output)]) == 2
    captured = capsys.readouterr()
    assert field + " must be finite" in captured.err and captured.out == ""
    assert path.read_bytes() == before and not output.exists()


def test_external_rules_extreme_limit_is_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "input.json"
    rules = tmp_path / "rules.json"
    path.write_text(json.dumps(backlog("hours", 1)), encoding="utf-8")
    rules.write_text(json.dumps({"max_hours": 10**400}), encoding="utf-8")
    before = (path.read_bytes(), rules.read_bytes())
    output = tmp_path / "report.json"
    assert (
        main(
            [
                str(path),
                "--seed",
                "rules",
                "--rules",
                str(rules),
                "--preview",
                "--output",
                str(output),
            ]
        )
        == 2
    )
    captured = capsys.readouterr()
    assert "max_hours must be finite" in captured.err and captured.out == ""
    assert (path.read_bytes(), rules.read_bytes()) == before and not output.exists()
