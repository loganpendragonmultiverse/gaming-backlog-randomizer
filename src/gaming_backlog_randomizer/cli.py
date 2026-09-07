from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import choose, load_backlog, render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Choose from a backlog with explicit rules.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--preview", action="store_true", help="Explain eligibility without drawing"
    )
    parser.add_argument("--history", type=Path, help="Local decision history JSON array")
    parser.add_argument(
        "--history-output", type=Path, help="Write a new history file after drawing"
    )
    parser.add_argument("--cooldown-days", type=int, default=0)
    parser.add_argument("--as-of", help="Explicit YYYY-MM-DD date for cooldowns/history")
    parser.add_argument(
        "--compare", type=Path, help="Alternative backlog/rules input for eligibility comparison"
    )
    args = parser.parse_args(argv)
    try:
        data = load_backlog(args.input)
        history = json.loads(args.history.read_text(encoding="utf-8")) if args.history else []
        if not isinstance(history, list):
            raise TypeError("history must be an array")
        data.update(history=history, cooldown_days=args.cooldown_days, as_of=args.as_of)
        report = choose(data, args.seed, args.count, preview=args.preview)
        if args.compare:
            alternative = load_backlog(args.compare)
            alternative.update(history=history, cooldown_days=args.cooldown_days, as_of=args.as_of)
            report["comparison"] = choose(alternative, args.seed, args.count, preview=True)
        if args.history_output:
            from datetime import date

            if args.preview or not args.as_of:
                raise ValueError("history output requires a draw and --as-of date")
            date.fromisoformat(args.as_of)
            if args.history_output.exists() or (
                args.output and args.history_output.resolve() == args.output.resolve()
            ):
                raise ValueError("history output must be a new distinct file")
            if args.output and args.output.exists():
                raise ValueError("output already exists")
        rendered = (
            json.dumps(report, indent=2, ensure_ascii=False) + "\n"
            if args.format == "json"
            else render_markdown(report)
        )
        if args.output:
            if args.output.exists():
                raise ValueError(f"output already exists: {args.output}")
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        if args.history_output:
            decisions = [
                {"id": game["id"], "date": args.as_of, "seed": args.seed}
                for game in report["selected"]
            ]
            args.history_output.write_text(
                json.dumps(history + decisions, indent=2) + "\n", encoding="utf-8"
            )
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
