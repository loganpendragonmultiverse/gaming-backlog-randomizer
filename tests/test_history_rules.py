import json

import pytest

from gaming_backlog_randomizer.cli import main
from gaming_backlog_randomizer.core import choose


@pytest.mark.parametrize(
    "history",
    [
        [17],
        [{"id": "a", "date": "not-a-date"}],
        [{"id": "a", "date": "20261016"}],
        [{"id": "a", "date": "2026-02-30"}],
        [{"id": False, "date": "2026-10-16"}],
        [{"id": "a"}],
    ],
)
@pytest.mark.parametrize("preview", [False, True])
def test_bad_history_rejected_without_cooldown_before_output(tmp_path, capsys, history, preview):
    source = tmp_path / "backlog.json"
    source.write_text(
        json.dumps({"version": 1, "games": [{"id": "a", "title": "Alpha", "platform": "PC"}]})
    )
    old = tmp_path / "old.json"
    old.write_text(json.dumps(history))
    before = (source.read_bytes(), old.read_bytes())
    output, new = tmp_path / "report.json", tmp_path / "history.json"
    args = [
        str(source),
        "--seed",
        "audit",
        "--history",
        str(old),
        "--as-of",
        "2026-10-17",
        "--output",
        str(output),
    ]
    if preview:
        args.append("--preview")
    else:
        args += ["--history-output", str(new)]
    assert main(args) == 2
    assert "history" in capsys.readouterr().err
    assert not output.exists() and not new.exists()
    assert before == (source.read_bytes(), old.read_bytes())


def test_history_extra_metadata_survives_append_and_later_cooldown(tmp_path, capsys):
    source = tmp_path / "backlog.json"
    source.write_text(
        json.dumps({"version": 1, "games": [{"id": "a", "title": "Alpha", "platform": "PC"}]})
    )
    prior = [{"id": "other", "date": "2026-10-01", "note": {"custom": [1, True]}}]
    old, new = tmp_path / "old.json", tmp_path / "new.json"
    old.write_text(json.dumps(prior))
    assert (
        main(
            [
                str(source),
                "--seed",
                "audit",
                "--history",
                str(old),
                "--as-of",
                "2026-10-17",
                "--history-output",
                str(new),
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert json.loads(new.read_text())[0] == prior[0]
    assert json.loads(old.read_text()) == prior
    assert (
        main(
            [
                str(source),
                "--seed",
                "audit",
                "--history",
                str(new),
                "--as-of",
                "2026-10-18",
                "--cooldown-days",
                "7",
                "--preview",
                "--format",
                "json",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["eligible_count"] == 0


def test_history_schema_is_checked_in_direct_preview_without_cooldown():
    with pytest.raises(TypeError, match="history"):
        choose({"games": [], "history": [17]}, "audit", preview=True)


def fixture(tmp_path):
    source = tmp_path / "games.csv"
    source.write_text("id,title,platform,hours,owned\na,Alpha,PC,2,true\nb,Beta,Console,30,false\n")
    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"platforms": ["PC"], "owned_only": True, "max_hours": 5}))
    return source, rules


def test_csv_rules_preview_draw_history_and_source_protection(tmp_path, capsys):
    source, rules = fixture(tmp_path)
    before = source.read_bytes(), rules.read_bytes()
    args = [
        str(source),
        "--seed",
        "audit",
        "--rules",
        str(rules),
        "--stable-ids",
        "--format",
        "json",
    ]
    assert main(args + ["--preview"]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert [x["id"] for x in preview["eligible"]] == ["a"]
    assert set(preview["excluded"][0]["reasons"]) == {"platform", "length", "not owned"}
    history = tmp_path / "history.json"
    assert main(args + ["--as-of", "2026-10-17", "--history-output", str(history)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["selected"][0]["id"] == "a"
    assert json.loads(history.read_text())[0]["id"] == "a"
    assert before == (source.read_bytes(), rules.read_bytes())


def test_rules_override_primary_json_and_keep_comparison_rules(tmp_path, capsys):
    _, rules = fixture(tmp_path)
    data = {
        "version": 1,
        "games": [
            {"id": "a", "title": "Alpha", "platform": "PC", "hours": 2, "owned": True},
            {"id": "b", "title": "Beta", "platform": "Console", "hours": 1, "owned": True},
        ],
        "rules": {"platforms": ["Console"]},
    }
    primary, alternative = tmp_path / "main.json", tmp_path / "alternative.json"
    primary.write_text(json.dumps(data))
    alternative.write_text(json.dumps(data))
    assert (
        main(
            [
                str(primary),
                "--seed",
                "audit",
                "--rules",
                str(rules),
                "--compare",
                str(alternative),
                "--preview",
                "--format",
                "json",
            ]
        )
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert [g["id"] for g in report["eligible"]] == ["a"]
    assert [g["id"] for g in report["comparison"]["eligible"]] == ["b"]
    assert json.loads(primary.read_text()) == data


@pytest.mark.parametrize(
    "value", [None, [], False, {"max_hours": "short"}, {"owned_only": "yes"}, {"platforms": "PC"}]
)
def test_invalid_rules_file_creates_no_outputs(tmp_path, capsys, value):
    source, rules = fixture(tmp_path)
    rules.write_text(json.dumps(value))
    output, history = tmp_path / "report.json", tmp_path / "history.json"
    assert (
        main(
            [
                str(source),
                "--seed",
                "audit",
                "--rules",
                str(rules),
                "--output",
                str(output),
                "--as-of",
                "2026-10-17",
                "--history-output",
                str(history),
            ]
        )
        == 2
    )
    capsys.readouterr()
    assert not output.exists() and not history.exists()
