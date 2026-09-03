#!/usr/bin/env python3
"""Fail unless every Level 4 lesson item is complete, ordered, and paged."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "level-4" / "lesson-content.json"
SUPPORT_PATH = ROOT / "level-4" / "supporting-content.json"
EXERCISE_PATH = ROOT / "level-4" / "exercise-content.json"
MANIFEST_PATH = ROOT / "level-4" / "source-manifest.json"
LINE_TRANSLATIONS_DIR = ROOT / "level-4" / "line-translations"
PAGE_BY_LESSON = {1: "l1-2.html", 2: "l1-2.html", 3: "l3-4.html", 4: "l3-4.html", 5: "l5-6.html", 6: "l5-6.html", 7: "l7-8.html", 8: "l7-8.html"}
MAIN_PAGE_RANGES = {
    1: [(1, 7, 7), (8, 13, 8)], 2: [(1, 8, 20), (9, 20, 21)],
    3: [(1, 10, 37), (11, 16, 38)], 4: [(1, 4, 48), (5, 8, 49)],
    5: [(1, 11, 63), (12, 15, 64)], 6: [(1, 6, 74), (7, 12, 75)],
    7: [(1, 9, 89), (10, 11, 90)], 8: [(1, 5, 99)],
}
LESSON_PAGE_BOUNDS = {1: (7, 19), 2: (20, 30), 3: (37, 47), 4: (48, 56), 5: (63, 73), 6: (74, 83), 7: (89, 98), 8: (99, 110)}
EXPECTED_COUNTS = {
    1: {"main": 13, "vocabulary": 19, "notes": 6, "grammar": 7, "exercise": 6},
    2: {"main": 20, "vocabulary": 37, "notes": 0, "grammar": 9, "exercise": 4},
    3: {"main": 16, "vocabulary": 17, "notes": 5, "grammar": 15, "exercise": 4},
    4: {"main": 8, "vocabulary": 27, "notes": 0, "grammar": 7, "exercise": 4},
    5: {"main": 15, "vocabulary": 12, "notes": 9, "grammar": 6, "exercise": 4},
    6: {"main": 12, "vocabulary": 48, "notes": 0, "grammar": 6, "exercise": 3},
    7: {"main": 11, "vocabulary": 25, "notes": 6, "grammar": 5, "exercise": 3},
    8: {"main": 5, "vocabulary": 36, "notes": 0, "grammar": 5, "exercise": 8},
}
EXPECTED_LAYOUT = {
    1: [("main", 1, 13), ("vocabulary", 1, 19), ("notes", 1, 6), ("exercise", 1, 2), ("grammar", 1, 1), ("exercise", 3, 3), ("grammar", 2, 2), ("exercise", 4, 4), ("grammar", 3, 7), ("exercise", 5, 6)],
    2: [("main", 1, 20), ("vocabulary", 1, 37), ("exercise", 1, 2), ("grammar", 1, 9), ("exercise", 3, 4)],
    3: [("main", 1, 16), ("vocabulary", 1, 17), ("notes", 1, 5), ("exercise", 1, 1), ("grammar", 1, 8), ("exercise", 2, 2), ("grammar", 9, 15), ("exercise", 3, 4)],
    4: [("main", 1, 8), ("vocabulary", 1, 27), ("exercise", 1, 1), ("grammar", 1, 2), ("exercise", 2, 2), ("grammar", 3, 7), ("exercise", 3, 4)],
    5: [("main", 1, 15), ("vocabulary", 1, 12), ("notes", 1, 9), ("exercise", 1, 2), ("grammar", 1, 3), ("exercise", 3, 3), ("grammar", 4, 6), ("exercise", 4, 4)],
    6: [("main", 1, 12), ("vocabulary", 1, 48), ("exercise", 1, 1), ("grammar", 1, 6), ("exercise", 2, 3)],
    7: [("main", 1, 11), ("vocabulary", 1, 25), ("notes", 1, 6), ("exercise", 1, 1), ("grammar", 1, 5), ("exercise", 2, 3)],
    8: [("main", 1, 5), ("vocabulary", 1, 36), ("exercise", 1, 2), ("grammar", 1, 1), ("exercise", 3, 3), ("grammar", 2, 2), ("exercise", 4, 4), ("grammar", 3, 3), ("exercise", 5, 5), ("grammar", 4, 4), ("exercise", 6, 6), ("grammar", 5, 5), ("exercise", 7, 8)],
}
REQUIRED_FIELDS = ("thai", "romanization", "zh-Hant", "en", "ja", "ko")
KANA = re.compile(r"[\u3040-\u30ff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")
HAN = re.compile(r"[\u3400-\u9fff]")


def main_page(lesson: int, sequence: int) -> str:
    for start, end, page in MAIN_PAGE_RANGES[lesson]:
        if start <= sequence <= end:
            return str(page)
    raise ValueError(f"No page for L{lesson} main #{sequence}")


def expected_page(lesson: int, category: str, sequence: int, unit: dict) -> str:
    page = str(unit["page"])
    if category == "main" and page != main_page(lesson, sequence):
        return f"INVALID:{page}"
    return page


def digest(units: list[dict], lesson: int, category: str) -> str:
    rows = []
    for sequence, unit in enumerate(units, start=1):
        rows.append("\t".join([
            expected_page(lesson, category, sequence, unit),
            unit["thai"],
            unit.get("thaiBody", ""),
        ]))
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def page_numbers(value: str) -> list[int]:
    match = re.fullmatch(r"(\d+)(?:[–-](\d+))?", value)
    if not match:
        return []
    start = int(match.group(1))
    end = int(match.group(2) or start)
    return list(range(start, end + 1)) if end >= start else []


def check_languages(unit: dict, label: str, errors: list[str]) -> None:
    for field in REQUIRED_FIELDS:
        if not str(unit.get(field, "")).strip():
            errors.append(f"{label}: missing {field}")
    zh = unit.get("zh-Hant", "")
    en = unit.get("en", "")
    ja = unit.get("ja", "")
    ko = unit.get("ko", "")
    if KANA.search(zh) or HANGUL.search(zh):
        errors.append(f"{label}: zh-Hant contains Japanese kana or Hangul")
    if KANA.search(en) or HANGUL.search(en) or HAN.search(en):
        errors.append(f"{label}: English contains CJK/Hangul text")
    if HANGUL.search(ja):
        errors.append(f"{label}: Japanese contains Hangul")
    if KANA.search(ko) or not HANGUL.search(ko):
        errors.append(f"{label}: Korean missing Hangul or contains Japanese kana")


def main() -> None:
    main_data = json.loads(MAIN_PATH.read_text(encoding="utf-8"))
    support_data = json.loads(SUPPORT_PATH.read_text(encoding="utf-8"))
    exercise_data = json.loads(EXERCISE_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    line_translations = {
        lesson: json.loads((LINE_TRANSLATIONS_DIR / f"lesson-{lesson}.json").read_text(encoding="utf-8"))
        for lesson in range(1, 9)
    }
    main_lessons = {item["lesson"]: item for item in main_data["lessons"]}
    support_lessons = {item["lesson"]: item for item in support_data["lessons"]}
    exercise_lessons = {item["lesson"]: item for item in exercise_data["lessons"]}
    frozen_lessons = {item["lesson"]: item for item in manifest["lessons"]}
    errors: list[str] = []
    total = 0
    total_content_rows = 0

    if any(sorted(items) != list(range(1, 9)) for items in (main_lessons, support_lessons, exercise_lessons)):
        errors.append("content data must contain Lessons 1–8 exactly once")

    for lesson in range(1, 9):
        main_lesson = main_lessons[lesson]
        support = support_lessons[lesson]
        exercise = exercise_lessons[lesson]
        lesson_translations = line_translations[lesson]
        if lesson_translations.get("lesson") != lesson:
            errors.append(f"L{lesson}: line translation file has wrong lesson number")
        used_translation_keys: set[str] = set()
        frozen = frozen_lessons.get(lesson, {}).get("categories", {})
        layout = [tuple(block) for block in exercise["layout"]]
        if layout != EXPECTED_LAYOUT[lesson]:
            errors.append(f"L{lesson}: layout inventory differs from verified textbook order")
        expected_order = [block[0] for block in EXPECTED_LAYOUT[lesson]]
        source_path = ROOT / "level-4" / PAGE_BY_LESSON[lesson]
        soup = BeautifulSoup(source_path.read_text(encoding="utf-8"), "html.parser")
        sections = soup.select(f'section[data-source-section] [data-source-lesson="{lesson}"]')
        lesson_sections = [
            section for section in soup.select("section[data-source-section]")
            if section.get("id", "").startswith(f"lesson-{lesson}-section-")
        ]
        rendered_order = [section.get("data-source-category") for section in lesson_sections]
        if rendered_order != expected_order:
            errors.append(f"L{lesson}: section order {rendered_order} != textbook order {expected_order}")

        categories = {
            "main": main_lesson["units"],
            "vocabulary": support["vocabulary"],
            "notes": support["notes"],
            "grammar": support["grammar"],
            "exercise": exercise["exercises"],
        }
        for category, units in categories.items():
            total += len(units)
            expected_count = EXPECTED_COUNTS[lesson][category]
            if len(units) != expected_count:
                errors.append(f"L{lesson} {category}: {len(units)} units != source inventory {expected_count}")
            frozen_category = frozen.get(category)
            if not frozen_category:
                errors.append(f"L{lesson} {category}: missing frozen manifest category")
            else:
                if frozen_category["unitCount"] != len(units):
                    errors.append(f"L{lesson} {category}: count differs from frozen manifest")
                if frozen_category["orderedPageAndThaiSha256"] != digest(units, lesson, category):
                    errors.append(f"L{lesson} {category}: page/order/source hash differs")

            rendered = [
                node for node in sections if node.get("data-source-category") == category
            ]
            if len(rendered) != len(units):
                errors.append(f"L{lesson} {category}: rendered {len(rendered)} != data {len(units)}")
                continue
            for sequence, (unit, node) in enumerate(zip(units, rendered), start=1):
                label = f"L{lesson} {category} #{sequence}"
                check_languages(unit, label, errors)
                page = expected_page(lesson, category, sequence, unit)
                numbers = page_numbers(page)
                low, high = LESSON_PAGE_BOUNDS[lesson]
                if not numbers or min(numbers) < low or max(numbers) > high:
                    errors.append(f"{label}: invalid/out-of-lesson page {page}")
                if node.get("data-source-sequence") != str(sequence):
                    errors.append(f"{label}: rendered sequence differs")
                if node.get("data-source-page") != page:
                    errors.append(f"{label}: rendered page differs")
                badge = node.select_one("[data-source-page-label]")
                expected_badge = ("pp. " if len(numbers) > 1 else "p. ") + page
                if not badge or badge.get_text(strip=True) != expected_badge:
                    errors.append(f"{label}: visible page label missing/differs")
                thai = node.select_one("[data-thai]")
                roman = node.select_one("[data-romanization]")
                if not thai or thai.get_text(strip=True) != unit["thai"]:
                    errors.append(f"{label}: rendered Thai heading differs")
                if not roman or roman.get_text(strip=True) != unit["romanization"]:
                    errors.append(f"{label}: rendered romanization differs")
                if category != "main":
                    expected_body = unit.get("thaiBody", "")
                    expected_roman_body = unit.get("romanizationBody", "")
                    if expected_body:
                        key = f"{category}-{sequence}"
                        used_translation_keys.add(key)
                        translated_lines = lesson_translations.get(key)
                        thai_lines = expected_body.splitlines()
                        roman_lines = expected_roman_body.splitlines()
                        if len(thai_lines) != len(roman_lines):
                            errors.append(f"{label}: Thai body and romanization line counts differ")
                        if not isinstance(translated_lines, list) or len(translated_lines) != len(thai_lines):
                            errors.append(f"{label}: line translation count differs")
                            translated_lines = []
                        rows = node.select(":scope > .sentence-row[data-content-unit]")
                        total_content_rows += len(rows)
                        if len(rows) != len(thai_lines) + 1:
                            errors.append(f"{label}: rendered sentence rows differ")
                        if node.select_one(".thai-source-body, .romanization-source-body"):
                            errors.append(f"{label}: legacy separated body layout remains")
                        for line_number, roman_line in enumerate(roman_lines, start=1):
                            if not re.search(r"[\u0E00-\u0E7F]", thai_lines[line_number - 1]):
                                continue
                            if not re.search(r"[A-Za-zÀ-žɯʉɔəɛ]", roman_line):
                                errors.append(f"{label}: romanization line {line_number} has no reading")
                            if re.search(r"[\u0E00-\u0E7F]|ò-ò|[a-zà-žɯʉɔəɛ]\d", roman_line):
                                errors.append(f"{label}: romanization line {line_number} contains a failed transcription marker")
                        for line_number, (thai_line, roman_line, translated, row) in enumerate(
                            zip(thai_lines, roman_lines, translated_lines, rows[1:]), start=1
                        ):
                            row_label = f"{label} line {line_number}"
                            if not isinstance(translated, list) or len(translated) != 4:
                                errors.append(f"{row_label}: translations must contain zh-Hant/en/ja/ko")
                                continue
                            translated_item = dict(zip(("zh-Hant", "en", "ja", "ko"), translated))
                            translated_item.update({"thai": thai_line, "romanization": roman_line})
                            check_languages(translated_item, row_label, errors)
                            if re.search(r"[\u0E00-\u0E7F]", thai_line):
                                row_thai = row.select_one("[data-thai]")
                                row_roman = row.select_one("[data-romanization]")
                                if not row_thai or row_thai.get_text() != thai_line:
                                    errors.append(f"{row_label}: rendered Thai differs")
                                if not row_roman or row_roman.get_text() != roman_line:
                                    errors.append(f"{row_label}: rendered romanization differs")
                                if row.select_one("[data-source-text]"):
                                    errors.append(f"{row_label}: Thai row incorrectly rendered as source text")
                            else:
                                source_text = row.select_one("[data-source-text]")
                                if not source_text or source_text.get_text() != thai_line:
                                    errors.append(f"{row_label}: rendered non-Thai source text differs")
                                if row.select_one("[data-thai], [data-romanization]"):
                                    errors.append(f"{row_label}: non-Thai source prompt has a fake Thai reading")
                            for language in ("zh-Hant", "en", "ja", "ko"):
                                translation = row.select_one(f'[data-translation="{language}"]')
                                if not translation or translation.get_text(strip=True) != translated_item[language]:
                                    errors.append(f"{row_label}: rendered {language} differs")
                    else:
                        total_content_rows += 1
                else:
                    total_content_rows += 1
                for language in ("zh-Hant", "en", "ja", "ko"):
                    translation = node.select_one(f'[data-translation="{language}"]')
                    expected_translation = (
                        unit[language].splitlines()[0]
                        if category != "main" and unit.get("thaiBody")
                        else unit[language]
                    )
                    if not translation or translation.get_text(strip=True) != expected_translation:
                        errors.append(f"{label}: rendered {language} differs")

        extra_translation_keys = set(lesson_translations) - {"lesson"} - used_translation_keys
        if extra_translation_keys:
            errors.append(f"L{lesson}: unused line translation keys {sorted(extra_translation_keys)}")

    if total != manifest.get("totalUnitCount"):
        errors.append(f"total {total} != manifest {manifest.get('totalUnitCount')}")
    if total != 443:
        errors.append(f"total {total} != source inventory 443")
    if total_content_rows != 1058:
        errors.append(f"sentence-aligned content rows {total_content_rows} != expected 1058")
    for path in [SUPPORT_PATH, EXERCISE_PATH, *[ROOT / "level-4" / f for f in set(PAGE_BY_LESSON.values())]]:
        source = path.read_text(encoding="utf-8")
        if "Error! Use the Home tab" in source:
            errors.append(f"{path.relative_to(ROOT)}: PDF extraction artifact leaked")
    if errors:
        raise SystemExit("SOURCE AUDIT FAILED\n- " + "\n- ".join(errors))

    summary = "; ".join(
        f"L{lesson}=" + "/".join(str(EXPECTED_COUNTS[lesson][c]) for c in ("main", "vocabulary", "notes", "grammar", "exercise"))
        for lesson in range(1, 9)
    )
    print(f"SOURCE AUDIT PASSED: 443 units and 1058 sentence-aligned rows (main/vocab/notes/grammar/exercise; {summary})")


if __name__ == "__main__":
    main()
