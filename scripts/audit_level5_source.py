#!/usr/bin/env python3
"""Compare Level 5 source data, the frozen manifest, and rendered HTML.

Checks count, order, page, and exact Thai text per section and category. Fixed
counts live here too, so deleting a row and refreezing cannot hide a gap.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_level5 import PAGES, SOURCE, parse, vocabulary_row

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "level-5" / "source-freeze.json"
EXPECTED_COUNTS: dict[str, dict[str, int]] = {
    "1": {
        "main": 4,
        "vocabulary": 2,
        "exercise": 7,
        "grammar": 6,
        "listening": 1
    },
    "2": {
        "main": 1,
        "vocabulary": 2,
        "exercise": 7,
        "grammar": 2,
        "listening": 1
    },
    "3": {
        "main": 1,
        "vocabulary": 2,
        "exercise": 7,
        "grammar": 2,
        "listening": 1
    },
    "4": {
        "main": 1,
        "vocabulary": 2,
        "exercise": 7,
        "grammar": 3,
        "listening": 1
    },
    "5": {
        "main": 1,
        "exercise": 8,
        "vocabulary": 2,
        "grammar": 3,
        "listening": 1
    },
    "6": {
        "main": 1,
        "vocabulary": 2,
        "exercise": 7,
        "grammar": 1,
        "listening": 1
    },
    "7": {
        "main": 1,
        "vocabulary": 2,
        "exercise": 7,
        "grammar": 3,
        "listening": 1
    },
    "8": {
        "main": 1,
        "vocabulary": 2,
        "exercise": 7,
        "grammar": 3,
        "listening": 1
    },
    "review-1": {
        "exercise": 7,
        "listening": 1
    },
    "review-2": {
        "exercise": 8,
        "listening": 2
    },
    "review-3": {
        "exercise": 8,
        "listening": 1
    },
    "review-4": {
        "exercise": 7,
        "listening": 2
    },
    "review-5": {
        "exercise": 8,
        "listening": 5
    }
}


def key_of(data: dict) -> str:
    return f"review-{data['number']}" if data["kind"] == "review" else str(data["number"])


def units(data: dict) -> dict[str, list[tuple[str, list[str]]]]:
    """Category -> ordered (page, displayed source lines) for each source unit."""
    out: dict[str, list[tuple[str, list[str]]]] = {}
    for block in data["blocks"]:
        rows = [vocabulary_row(r) if block["category"] == "vocabulary" else r for r in block["rows"]]
        out.setdefault(block["category"], []).append((block["page"], [block["heading"][0], *[r[0] for r in rows]]))
    return out


def fingerprint(items: list[tuple[str, list[str]]]) -> dict:
    text = "\n".join(f"{page}\t{line}" for page, lines in items for line in lines)
    return {
        "unitCount": len(items),
        "rowCount": sum(len(lines) for _, lines in items),
        "orderedPageAndThaiSha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def all_sections() -> list[dict]:
    return [parse(p) for p in sorted(SOURCE.glob("*.txt"))]


def source_inventory() -> dict:
    return {key_of(d): {c: fingerprint(i) for c, i in units(d).items()} for d in all_sections()}


def rendered_units(text: str, key: str) -> dict[str, list[tuple[str, list[str]]]]:
    out: dict[str, list[tuple[str, list[str]]]] = {}
    pattern = re.compile(
        rf'<article data-source-unit data-source-category="(\w+)" data-source-lesson="{re.escape(key)}" '
        r'data-source-sequence="\d+" data-source-page="([^"]+)">(.*?)</article>', re.S)
    for category, page, body in pattern.findall(text):
        lines = re.findall(r'<div data-(?:thai lang="th"|source-text lang="en")>(.*?)</div>', body, re.S)
        out.setdefault(category, []).append((page, [html.unescape(x) for x in lines]))
    return out


def main() -> int:
    failures: list[str] = []
    if not MANIFEST_PATH.exists():
        print("FAILED: source-freeze.json is missing")
        return 1
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["sections"]
    inventory = source_inventory()
    pages = {n: name for name, numbers in PAGES.items() for n in numbers}
    for data in all_sections():
        key = key_of(data)
        name = "exam-review.html" if data["kind"] == "review" else pages[data["number"]]
        rendered = rendered_units((ROOT / "level-5" / name).read_text(encoding="utf-8"), key if data["kind"] == "review" else str(data["number"]))
        for category, items in units(data).items():
            where = f"{key}/{category}"
            if manifest.get(key, {}).get(category) != inventory[key][category]:
                failures.append(f"{where}: differs from frozen manifest")
            expected = EXPECTED_COUNTS.get(key, {}).get(category)
            if expected != len(items):
                failures.append(f"{where}: {len(items)} units, fixed count is {expected}")
            if rendered.get(category) != items:
                failures.append(f"{where}: rendered HTML differs from source (count, order, page, or text)")
    for key in manifest:
        if key not in inventory:
            failures.append(f"{key}: in manifest but missing from source")
    for failure in failures:
        print("FAILED", failure)
    total = sum(c["rowCount"] for s in inventory.values() for c in s.values())
    print(f"Level 5 source audit: {'FAIL' if failures else 'PASS'} ({len(inventory)} sections, {total} rows, {len(failures)} issues)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
