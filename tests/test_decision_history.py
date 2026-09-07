import json
from pathlib import Path

import pytest

from gaming_backlog_randomizer.cli import main
from gaming_backlog_randomizer.core import choose, load_backlog


def test_readme_commands_and_preview(capsys) -> None:
    source = Path(__file__).parents[1] / "examples/backlog.json"
    assert main([str(source), "--seed", "weekend-26"]) == 0
    capsys.readouterr()
    assert main([str(source), "--seed", "weekend-26", "--count", "2", "--format", "json"]) == 0
    assert len(json.loads(capsys.readouterr().out)["selected"]) == 2
    report = choose(load_backlog(source), "demo", 999, preview=True)
    assert not report["selected"]
    assert sum(game["first_draw_probability"] for game in report["eligible"]) == pytest.approx(1)


def test_csv_history_cooldown_and_comparison(tmp_path, capsys) -> None:
    source = tmp_path / "games.csv"
    source.write_text(
        "id,title,platform,genres,moods,hours,weight,owned\na,Alpha,PC,rpg|puzzle,calm,2,2,true\nb,Beta,PC,puzzle,calm,,,false\n"
    )
    history = tmp_path / "history.json"
    assert (
        main(
            [str(source), "--seed", "x", "--as-of", "2026-09-07", "--history-output", str(history)]
        )
        == 0
    )
    capsys.readouterr()
    assert len(json.loads(history.read_text())) == 1
    assert (
        main(
            [
                str(source),
                "--seed",
                "x",
                "--history",
                str(history),
                "--as-of",
                "2026-09-08",
                "--cooldown-days",
                "7",
                "--preview",
                "--compare",
                str(source),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "Alternative eligibility preview" in output and "recently played" in output
    data = load_backlog(source)
    data.update(history=json.loads(history.read_text()), as_of="2026-09-15", cooldown_days=7)
    assert choose(data, "x", preview=True)["eligible_count"] == 2


@pytest.mark.parametrize(
    "options",
    [
        {"cooldown_days": -1},
        {"cooldown_days": 1},
        {"cooldown_days": 1, "as_of": "2026-09-07", "history": {}},
        {"cooldown_days": 1, "as_of": "2026-09-07", "history": [None]},
        {"cooldown_days": 1, "as_of": "2026-09-07", "history": [{"id": "a", "date": "2026-09-08"}]},
    ],
)
def test_invalid_history_contract(options) -> None:
    with pytest.raises((ValueError, TypeError)):
        choose({"games": [], **options}, "x", preview=True)


def test_history_output_protection(tmp_path, capsys) -> None:
    source = tmp_path / "games.csv"
    source.write_text("id,title,platform,owned\na,Alpha,PC,true\n")
    output = tmp_path / "history.json"
    assert main([str(source), "--seed", "x", "--preview", "--history-output", str(output)]) == 2
    output.write_text("[]")
    assert (
        main([str(source), "--seed", "x", "--as-of", "2026-09-07", "--history-output", str(output)])
        == 2
    )
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    assert main([str(source), "--seed", "x", "--history", str(bad)]) == 2
    source.write_text("id,title,platform,owned\na,Alpha,PC,maybe\n")
    with pytest.raises(ValueError, match="owned"):
        load_backlog(source)
