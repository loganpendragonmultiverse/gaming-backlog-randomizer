import json
from pathlib import Path

import pytest

from gaming_backlog_randomizer.cli import main
from gaming_backlog_randomizer.core import load_backlog


@pytest.mark.parametrize("limit", [float("nan"), float("inf"), float("-inf"), True, -1])
def test_nonfinite_or_invalid_hard_limits_rejected(tmp_path: Path, capsys, limit):
    path = tmp_path / "backlog.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "games": [{"id": "one", "title": "One", "platform": "PC", "hours": 8}],
                "rules": {"max_hours": limit},
            }
        )
    )
    with pytest.raises(ValueError, match="finite"):
        load_backlog(path)
    assert main([str(path), "--seed", "fixture"]) == 2
    assert "max_hours" in capsys.readouterr().err
