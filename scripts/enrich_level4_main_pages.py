#!/usr/bin/env python3
"""Persist the verified printed-page mapping on every Level 4 main source unit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "level-4" / "lesson-content.json"
PAGE_RANGES = {
    1: [(1, 7, 7), (8, 13, 8)], 2: [(1, 8, 20), (9, 20, 21)],
    3: [(1, 10, 37), (11, 16, 38)], 4: [(1, 4, 48), (5, 8, 49)],
    5: [(1, 11, 63), (12, 15, 64)], 6: [(1, 6, 74), (7, 12, 75)],
    7: [(1, 9, 89), (10, 11, 90)], 8: [(1, 5, 99)],
}


def page_for(lesson: int, sequence: int) -> str:
    for start, end, page in PAGE_RANGES[lesson]:
        if start <= sequence <= end:
            return str(page)
    raise ValueError(f"No page for L{lesson} main #{sequence}")


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    for lesson in data["lessons"]:
        for sequence, unit in enumerate(lesson["units"], start=1):
            unit["page"] = page_for(lesson["lesson"], sequence)
    data["schemaVersion"] = 2
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Enriched {PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
