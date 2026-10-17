import json
from pathlib import Path

import pytest

from gaming_backlog_randomizer.cli import main
from gaming_backlog_randomizer.core import choose


def backlog(weights=(1, 1)):
    return {
        "version": 1,
        "games": [
            {"id": str(i), "title": str(i), "platform": "PC", "weight": weight}
            for i, weight in enumerate(weights)
        ],
    }


@pytest.mark.parametrize("preview", [False, True])
def test_finite_weights_with_overflowing_total_are_rejected_before_output(
    tmp_path: Path, capsys, preview
):
    source = tmp_path / "backlog.json"
    source.write_text(json.dumps(backlog((1e308, 1e308))))
    before = source.read_bytes()
    output = tmp_path / "report.json"
    args = [str(source), "--seed", "review", "--output", str(output)]
    if preview:
        args.append("--preview")
    assert main(args) == 2
    assert "eligible total weight must be finite; use smaller weights" in capsys.readouterr().err
    assert not output.exists() and source.read_bytes() == before


def test_single_large_weight_and_ordinary_probabilities_still_work():
    assert choose(backlog((1e308,)), "review")["selected"][0]["id"] == "0"
    assert (
        choose(backlog((1e308,)), "review", preview=True)["eligible"][0]["first_draw_probability"]
        == 1
    )
    assert [
        x["first_draw_probability"]
        for x in choose(backlog((1, 3)), "review", preview=True)["eligible"]
    ] == [0.25, 0.75]


@pytest.mark.parametrize("value", ["20261017", "2026-W42-6", "2026-02-30", ""])
def test_as_of_is_canonical_even_without_cooldown(value):
    with pytest.raises(ValueError, match="as_of must be YYYY-MM-DD"):
        choose({**backlog(), "as_of": value}, "review")


@pytest.mark.parametrize("value", ["20261016", "2026-W42-5", "2026-02-30"])
def test_cooldown_history_dates_are_canonical(value):
    with pytest.raises(ValueError, match="history date must be YYYY-MM-DD"):
        choose(
            {
                **backlog(),
                "as_of": "2026-10-17",
                "cooldown_days": 1,
                "history": [{"id": "0", "date": value}],
            },
            "review",
            preview=True,
        )


@pytest.mark.parametrize("ignored", ["first note", {"nested": True}, [{"nested": "note"}]])
def test_ignored_rule_metadata_does_not_change_effective_identity(ignored):
    base = backlog()
    base["rules"] = {"platforms": ["PC"]}
    first = choose(base, "review", stable_ids=True)
    base["rules"]["notes"] = ignored
    other = choose(base, "review", stable_ids=True)
    assert first["input_identity"] == other["input_identity"]
    assert [x["id"] for x in first["selected"]] == [x["id"] for x in other["selected"]]
