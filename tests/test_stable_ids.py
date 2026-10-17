import copy
import json

import pytest

from gaming_backlog_randomizer.cli import main
from gaming_backlog_randomizer.core import choose


def data():
    return {
        "version": 1,
        "games": [
            {"id": i, "title": i, "platform": "PC", "weight": w, "genres": ["b", "a"], "moods": []}
            for i, w in [("z", 5), ("a", 1), ("m", 3)]
        ],
    }


def test_reordered_weighted_multi_draw_and_identity():
    original = data()
    other = copy.deepcopy(original)
    other["games"].reverse()
    other["games"][0]["genres"].reverse()
    for seed in ["weekend", "another", "", "é"]:
        a = choose(original, seed, 3, stable_ids=True)
        b = choose(other, seed, 3, stable_ids=True)
        assert [g["id"] for g in a["selected"]] == [g["id"] for g in b["selected"]]
        assert a["input_identity"] == b["input_identity"]
    assert original == data()


def test_changed_input_identity_and_legacy_order():
    a = data()
    b = copy.deepcopy(a)
    b["games"][0]["weight"] = 4
    assert (
        choose(a, "s", stable_ids=True)["input_identity"]
        != choose(b, "s", stable_ids=True)["input_identity"]
    )
    assert [g["id"] for g in choose(a, "s", preview=True)["eligible"]] == ["z", "a", "m"]
    assert choose(a, "s")["selection_mode"] == "input-order-v1"
    assert choose(a, "s")["input_identity"] is None


def test_cooldown_preview_and_compare_cli(tmp_path, capsys):
    d = data()
    d.update(history=[{"id": "a", "date": "2026-10-16"}], cooldown_days=7, as_of="2026-10-17")
    r = choose(d, "s", preview=True, stable_ids=True)
    assert r["selected"] == []
    assert r["excluded"][0]["id"] == "a"
    path = tmp_path / "backlog.json"
    path.write_text(json.dumps(data()))
    assert (
        main([str(path), "--seed", "s", "--stable-ids", "--compare", str(path), "--format", "json"])
        == 0
    )
    out = json.loads(capsys.readouterr().out)
    assert out["comparison"]["input_identity"] == out["input_identity"]


@pytest.mark.parametrize("ids", [["a", "a"], ["", "a"], [" ", "a"]])
def test_stable_ids_required(ids):
    d = data()
    d["games"] = d["games"][:2]
    for game, i in zip(d["games"], ids):
        game["id"] = i
    with pytest.raises(ValueError, match="unique non-empty"):
        choose(d, "s", stable_ids=True)
