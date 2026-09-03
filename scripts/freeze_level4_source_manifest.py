#!/usr/bin/env python3
"""Deliberately freeze Level 4 counts, pages, source text, and order."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "level-4" / "lesson-content.json"
SUPPORT_PATH = ROOT / "level-4" / "supporting-content.json"
EXERCISE_PATH = ROOT / "level-4" / "exercise-content.json"
MANIFEST_PATH = ROOT / "level-4" / "source-manifest.json"
MAIN_PAGE_RANGES = {
    1: [(1, 7, 7), (8, 13, 8)], 2: [(1, 8, 20), (9, 20, 21)],
    3: [(1, 10, 37), (11, 16, 38)], 4: [(1, 4, 48), (5, 8, 49)],
    5: [(1, 11, 63), (12, 15, 64)], 6: [(1, 6, 74), (7, 12, 75)],
    7: [(1, 9, 89), (10, 11, 90)], 8: [(1, 5, 99)],
}


def main_page(lesson: int, sequence: int) -> str:
    for start, end, page in MAIN_PAGE_RANGES[lesson]:
        if start <= sequence <= end:
            return str(page)
    raise ValueError(f"No page mapping for L{lesson} main #{sequence}")


def digest(units: list[dict], lesson: int, category: str) -> str:
    rows = []
    for sequence, unit in enumerate(units, start=1):
        page = str(unit["page"])
        if category == "main" and page != main_page(lesson, sequence):
            raise ValueError(f"Unexpected source page {page} for L{lesson} main #{sequence}")
        rows.append("\t".join([page, unit["thai"], unit.get("thaiBody", "")]))
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def main() -> None:
    main_data = json.loads(MAIN_PATH.read_text(encoding="utf-8"))
    support_data = json.loads(SUPPORT_PATH.read_text(encoding="utf-8"))
    exercise_data = json.loads(EXERCISE_PATH.read_text(encoding="utf-8"))
    support = {item["lesson"]: item for item in support_data["lessons"]}
    exercise = {item["lesson"]: item for item in exercise_data["lessons"]}
    lessons = []
    total = 0
    for lesson in main_data["lessons"]:
        number = lesson["lesson"]
        categories = {}
        for category, units in (
            ("main", lesson["units"]),
            ("vocabulary", support[number]["vocabulary"]),
            ("notes", support[number]["notes"]),
            ("grammar", support[number]["grammar"]),
            ("exercise", exercise[number]["exercises"]),
        ):
            categories[category] = {
                "unitCount": len(units),
                "orderedPageAndThaiSha256": digest(units, number, category),
            }
            total += len(units)
        lessons.append({"lesson": number, "kind": lesson["kind"], "categories": categories})
    manifest = {
        "schemaVersion": 2,
        "scope": "level-4-lessons-1-8-complete-textbook-order",
        "totalUnitCount": total,
        "lessons": lessons,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Frozen {MANIFEST_PATH.relative_to(ROOT)} with {total} units")


if __name__ == "__main__":
    main()
