#!/usr/bin/env python3
"""Verify every Thai source line against its declared textbook PDF page.

Usage: python verify_level4_against_pdf.py /path/to/textbook.pdf
The source PDF remains local and is never copied into the repository.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "level-4" / "lesson-content.json"
SUPPORT_PATH = ROOT / "level-4" / "supporting-content.json"
EXERCISE_PATH = ROOT / "level-4" / "exercise-content.json"
MAIN_PAGE_RANGES = {
    1: [(1, 7, 7), (8, 13, 8)], 2: [(1, 8, 20), (9, 20, 21)],
    3: [(1, 10, 37), (11, 16, 38)], 4: [(1, 4, 48), (5, 8, 49)],
    5: [(1, 11, 63), (12, 15, 64)], 6: [(1, 6, 74), (7, 12, 75)],
    7: [(1, 9, 89), (10, 11, 90)], 8: [(1, 5, 99)],
}
MARKS = str.maketrans("ำ่้๊๋์ํ", "า      ")


def normalize_thai(text: str) -> str:
    text = text.translate(MARKS)
    return "".join(re.findall(r"[\u0E01-\u0E2E\u0E30-\u0E4E]", text)).replace(" ", "")


def pages(value: str) -> list[int]:
    match = re.fullmatch(r"(\d+)(?:[–-](\d+))?", value)
    if not match:
        return []
    start, end = int(match.group(1)), int(match.group(2) or match.group(1))
    return list(range(start, end + 1))


def main_page(lesson: int, sequence: int) -> str:
    for start, end, page in MAIN_PAGE_RANGES[lesson]:
        if start <= sequence <= end:
            return str(page)
    raise ValueError(f"No page for L{lesson} main #{sequence}")


def check_line(line: str, source: str) -> bool:
    normalized = normalize_thai(line)
    return len(normalized) < 4 or normalized in source


def is_example_anchor(line: str) -> bool:
    if re.search(r"หมายถึง|แสดง|ใช้กับ|แสดงผู้รับ|แสดงเป้าหมาย", line):
        return False
    return bool(re.match(r"^\s*(?:\d+\)|-\s|[กข]:|คนไข้:|หมอ:)", line))


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_level4_against_pdf.py /path/to/textbook.pdf")
    reader = PdfReader(sys.argv[1])
    extracted = {
        page: normalize_thai(reader.pages[page].extract_text(extraction_mode="layout") or "")
        for page in range(7, 111)
    }
    main_data = json.loads(MAIN_PATH.read_text(encoding="utf-8"))
    support_data = json.loads(SUPPORT_PATH.read_text(encoding="utf-8"))
    exercise_data = json.loads(EXERCISE_PATH.read_text(encoding="utf-8"))
    support = {item["lesson"]: item for item in support_data["lessons"]}
    exercises = {item["lesson"]: item["exercises"] for item in exercise_data["lessons"]}
    failures = []
    checked = 0
    for lesson_data in main_data["lessons"]:
        lesson = lesson_data["lesson"]
        for sequence, unit in enumerate(lesson_data["units"], start=1):
            page = str(unit["page"])
            if page != main_page(lesson, sequence):
                failures.append(f"L{lesson} main #{sequence}: wrong declared page {page}")
            source = "".join(extracted[n] for n in pages(page))
            checked += 1
            if not check_line(unit["thai"], source):
                failures.append(f"L{lesson} main #{sequence} p.{page}: {unit['thai']}")
        for category in ("vocabulary", "notes", "grammar"):
            for sequence, unit in enumerate(support[lesson][category], start=1):
                page = str(unit["page"])
                source = "".join(extracted[n] for n in pages(page))
                lines = [unit["thai"], *unit.get("thaiBody", "").splitlines()]
                unit_matches = 0
                for line_number, line in enumerate(lines, start=1):
                    checked += 1
                    normalized = normalize_thai(line)
                    matches = len(normalized) >= 1 and normalized in source
                    unit_matches += int(matches and len(normalize_thai(line)) >= 4)
                    if category == "vocabulary" and line_number == 1 and not matches:
                        failures.append(
                            f"L{lesson} {category} #{sequence} p.{page}: {line}"
                        )
                    elif is_example_anchor(line) and not matches:
                        failures.append(
                            f"L{lesson} {category} #{sequence} p.{page} line {line_number}: {line}"
                        )
                if category != "vocabulary" and not unit_matches:
                    failures.append(
                        f"L{lesson} {category} #{sequence} p.{page}: no Thai source anchor matched"
                    )
        for sequence, unit in enumerate(exercises[lesson], start=1):
            page = str(unit["page"])
            source = "".join(extracted[n] for n in pages(page))
            for line_number, line in enumerate(unit["thaiBody"].splitlines(), start=1):
                normalized = normalize_thai(line)
                if len(normalized) < 4:
                    continue
                checked += 1
                if normalized not in source:
                    failures.append(
                        f"L{lesson} exercise #{sequence} p.{page} line {line_number}: {line}"
                    )
    if failures:
        raise SystemExit(
            f"PDF SOURCE VERIFICATION FAILED: {len(failures)} of {checked} lines\n- "
            + "\n- ".join(failures)
        )
    print(f"PDF SOURCE VERIFICATION PASSED: {checked} Thai lines checked; every unit/page, supporting example, and exercise source line matched")


if __name__ == "__main__":
    main()
