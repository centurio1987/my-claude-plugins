#!/usr/bin/env python3
"""Score a react-mdx-diagram quality-gate run against the CONTRACT §9 rubric.

INPUT — a JSON file (path as argv[1], default ./score-input.json) shaped like:

    {
      "dimensions": [
        {
          "id": 1,
          "name": "DNA fidelity",
          "points": 25,
          "critical": true,
          "items": [
            {"name": "All 8 palette hexes present and unaltered", "points": 8, "pass": true},
            {"name": "5 node taxonomy fills correct", "points": 7, "pass": false},
            ...
          ]
        },
        ...
      ],
      "playwright_green": true,
      "check_mdx_green": true
    }

Each dimension's earned points = sum of passed items, capped at the dimension's
"points" budget. Missing keys default to failing (safe-pessimistic).

The gate orchestrator supplies this JSON after running the Playwright suite and
check_mdx.py. This script's exit code (0=PASS, 1=FAIL) is what the gate loop
reads to decide whether to spawn fix agents.

Output is machine-parseable:
  - One header line per dimension with earned/possible.
  - A TOTAL line.
  - A PASS/FAIL verdict line (prefix "RESULT:").
  - A "FAILURES:" section listing every failed item, grouped by dimension
    (used by the orchestrator to dispatch fix agents).

Usage:
    python3 score.py [score-input.json] [--threshold N]

Threshold defaults to 85 (CONTRACT §9). Override with --threshold N.
"""
import json
import sys
from pathlib import Path

DEFAULT_INPUT = "./score-input.json"
DEFAULT_THRESHOLD = 85

# Dimensions that must not score 0 (CRITICAL per CONTRACT §9).
CRITICAL_IDS = {1, 2, 3, 5}


def load_input(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: input file not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {path}: {exc}", file=sys.stderr)
        raise SystemExit(1)


def parse_args():
    args = sys.argv[1:]
    threshold = DEFAULT_THRESHOLD
    input_path = DEFAULT_INPUT
    i = 0
    while i < len(args):
        if args[i] == "--threshold":
            i += 1
            if i >= len(args):
                print("ERROR: --threshold requires a value", file=sys.stderr)
                raise SystemExit(1)
            try:
                threshold = int(args[i])
            except ValueError:
                print(f"ERROR: --threshold value must be an integer, got: {args[i]}", file=sys.stderr)
                raise SystemExit(1)
        else:
            input_path = args[i]
        i += 1
    return input_path, threshold


def score_dimension(dim: dict) -> tuple[int, list[str]]:
    """Return (earned_points, list_of_failed_item_names).

    Points are summed from passed items and capped at dim["points"].
    Missing or non-bool "pass" values are treated as False (safe-pessimistic).
    """
    cap = int(dim.get("points", 0))
    items = dim.get("items", [])
    earned = 0
    failed = []
    for item in items:
        name = item.get("name", "<unnamed item>")
        pts = int(item.get("points", 0))
        passed = item.get("pass")
        if passed is True:
            earned += pts
        else:
            failed.append(f"{name} ({pts}pt{'s' if pts != 1 else ''})")
    earned = min(earned, cap)
    return earned, failed


def main() -> int:
    input_path, threshold = parse_args()
    data = load_input(input_path)

    playwright_green = data.get("playwright_green", False) is True
    check_mdx_green = data.get("check_mdx_green", False) is True
    dimensions = data.get("dimensions", [])

    total_earned = 0
    total_possible = 0
    all_failures: list[tuple[str, list[str]]] = []  # (dim_label, [failed_items])
    critical_zeroed: list[str] = []

    col_w = 45
    print("")
    print(f"{'DIMENSION':<{col_w}}  {'EARNED':>6}  {'MAX':>5}")
    print("-" * (col_w + 16))

    for dim in dimensions:
        dim_id = int(dim.get("id", 0))
        dim_name = dim.get("name", f"Dimension {dim_id}")
        dim_points = int(dim.get("points", 0))
        is_critical = dim.get("critical", dim_id in CRITICAL_IDS)

        earned, failed_items = score_dimension(dim)
        total_earned += earned
        total_possible += dim_points

        critical_marker = " [CRITICAL]" if is_critical else ""
        label = f"#{dim_id} {dim_name}{critical_marker}"
        print(f"{label:<{col_w}}  {earned:>6}  {dim_points:>5}")

        if failed_items:
            all_failures.append((f"#{dim_id} {dim_name}", failed_items))

        if is_critical and earned == 0:
            critical_zeroed.append(f"#{dim_id} {dim_name}")

    print("-" * (col_w + 16))
    print(f"{'TOTAL':<{col_w}}  {total_earned:>6}  {total_possible:>5}")
    print("")
    print(f"playwright_green : {'YES' if playwright_green else 'NO'}")
    print(f"check_mdx_green  : {'YES' if check_mdx_green else 'NO'}")
    print("")

    # Evaluate gate rule (CONTRACT §9):
    # PASS iff total >= threshold AND no critical dim zeroed AND playwright green AND check_mdx green
    gate_pass = (
        total_earned >= threshold
        and not critical_zeroed
        and playwright_green
        and check_mdx_green
    )

    if gate_pass:
        print(f"RESULT: PASS  ({total_earned}/{threshold} threshold met, all gates green)")
    else:
        reasons = []
        if total_earned < threshold:
            reasons.append(f"score {total_earned} < threshold {threshold}")
        for dim_label in critical_zeroed:
            reasons.append(f"CRITICAL dimension zeroed: {dim_label}")
        if not playwright_green:
            reasons.append("playwright_green is false")
        if not check_mdx_green:
            reasons.append("check_mdx_green is false")
        print(f"RESULT: FAIL  ({'; '.join(reasons)})")

    if all_failures:
        print("")
        print("FAILURES:")
        for dim_label, items in all_failures:
            print(f"  {dim_label}:")
            for item in items:
                print(f"    - {item}")

    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
