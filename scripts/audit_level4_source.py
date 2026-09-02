#!/usr/bin/env python3
"""Fail unless Level 4 content, frozen manifest, and rendered pages match exactly."""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "level-4" / "lesson-content.json"
MANIFEST_PATH = ROOT / "level-4" / "source-manifest.json"
PAGE_BY_LESSON = {1: "l1-2.html", 2: "l1-2.html", 3: "l3-4.html", 4: "l3-4.html", 5: "l5-6.html", 6: "l5-6.html", 7: "l7-8.html", 8: "l7-8.html"}
REQUIRED_FIELDS = ("thai", "romanization", "zh-Hant", "en", "ja", "ko")


def digest(units: list[dict[str, str]]) -> str:
    return hashlib.sha256("\n".join(unit["thai"] for unit in units).encode("utf-8")).hexdigest()


def main() -> None:
    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_lessons = {item["lesson"]: item for item in manifest["lessons"]}
    errors: list[str] = []
    total = 0

    for lesson in content["lessons"]:
        number = lesson["lesson"]
        units = lesson["units"]
        total += len(units)
        frozen = manifest_lessons.get(number)
        if not frozen:
            errors.append(f"L{number}: missing from frozen manifest")
            continue
        if frozen["unitCount"] != len(units):
            errors.append(f"L{number}: count {len(units)} != frozen {frozen['unitCount']}")
        if frozen["orderedThaiSha256"] != digest(units):
            errors.append(f"L{number}: ordered Thai hash differs from frozen source")

        for sequence, unit in enumerate(units, start=1):
            for field in REQUIRED_FIELDS:
                if not unit.get(field, "").strip():
                    errors.append(f"L{number} #{sequence}: missing {field}")

        page = (ROOT / "level-4" / PAGE_BY_LESSON[number]).read_text(encoding="utf-8")
        section_match = re.search(
            rf'<section class="lesson-section" id="lesson-{number}-section-1" data-source-section>(.*?)</section>',
            page,
            re.DOTALL,
        )
        if not section_match:
            errors.append(f"L{number}: rendered source section missing")
            continue
        section = section_match.group(1)
        rendered_thai = [html.unescape(value) for value in re.findall(r'<div data-thai lang="th">(.*?)</div>', section, re.DOTALL)]
        expected_thai = [unit["thai"] for unit in units]
        if rendered_thai != expected_thai:
            errors.append(f"L{number}: rendered Thai text/count/order differs from content data")
        source_sequences = [int(value) for value in re.findall(r'data-source-sequence="(\d+)"', section)]
        if source_sequences != list(range(1, len(units) + 1)):
            errors.append(f"L{number}: rendered source sequence is incomplete or reordered")

    if total != manifest["totalUnitCount"]:
        errors.append(f"total count {total} != frozen {manifest['totalUnitCount']}")
    if errors:
        raise SystemExit("SOURCE AUDIT FAILED\n- " + "\n- ".join(errors))

    counts = ", ".join(f"L{item['lesson']}={item['unitCount']}" for item in manifest["lessons"])
    print(f"SOURCE AUDIT PASSED: {total} units ({counts})")


if __name__ == "__main__":
    main()
