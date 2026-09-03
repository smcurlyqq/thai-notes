#!/usr/bin/env python3
"""Render all Level 4 lesson content in exact textbook order."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_CONTENT_PATH = ROOT / "level-4" / "lesson-content.json"
SUPPORTING_CONTENT_PATH = ROOT / "level-4" / "supporting-content.json"
EXERCISE_CONTENT_PATH = ROOT / "level-4" / "exercise-content.json"
LINE_TRANSLATIONS_DIR = ROOT / "level-4" / "line-translations"
PAGE_BY_LESSON = {
    1: "l1-2.html", 2: "l1-2.html", 3: "l3-4.html", 4: "l3-4.html",
    5: "l5-6.html", 6: "l5-6.html", 7: "l7-8.html", 8: "l7-8.html",
}
MAIN_PAGE_RANGES = {
    1: [(1, 7, 7), (8, 13, 8)],
    2: [(1, 8, 20), (9, 20, 21)],
    3: [(1, 10, 37), (11, 16, 38)],
    4: [(1, 4, 48), (5, 8, 49)],
    5: [(1, 11, 63), (12, 15, 64)],
    6: [(1, 6, 74), (7, 12, 75)],
    7: [(1, 9, 89), (10, 11, 90)],
    8: [(1, 5, 99)],
}
SECTION_HEADINGS = {
    "vocabulary": ("完整單字", "Complete vocabulary"),
    "notes": ("課本註解", "Textbook notes"),
    "grammar": ("課本文法", "Textbook grammar"),
    "exercise": ("課本練習", "Textbook exercises"),
}
THAI_LETTER_RE = re.compile(r"[\u0E01-\u0E2E\u0E30-\u0E3A\u0E40-\u0E4E]")


def escaped(value: str) -> str:
    return html.escape(value, quote=True)


def main_page(lesson: int, sequence: int) -> str:
    for start, end, page in MAIN_PAGE_RANGES[lesson]:
        if start <= sequence <= end:
            return str(page)
    raise ValueError(f"No source page for L{lesson} main unit {sequence}")


def page_badge(page: str) -> str:
    prefix = "pp." if "–" in page or "-" in page else "p."
    return f'<span class="source-page" data-source-page-label>{prefix} {escaped(page)}</span>'


def render_translation(item: dict[str, str], language: str, extra: bool = False) -> str:
    attribute = " data-extra-language" if extra else ""
    return (
        f'<div class="translation-body" data-translation="{language}" '
        f'lang="{language}"{attribute}>{escaped(item[language])}</div>'
    )


def heading_translations(item: dict[str, str]) -> dict[str, str]:
    """Keep aggregate examples out of the source-heading row.

    Multi-line source items store a legacy summary followed by example
    translations. The examples are rendered sentence by sentence below the
    heading, so the heading row must contain only the leading explanation.
    """
    return {
        language: item[language].splitlines()[0]
        for language in ("zh-Hant", "en", "ja", "ko")
    }


def render_sentence_row(
    thai: str,
    romanization: str,
    translations: dict[str, str] | list[str],
    heading: bool = False,
) -> str:
    if isinstance(translations, list):
        translations = dict(zip(("zh-Hant", "en", "ja", "ko"), translations, strict=True))
    classes = "sentence-row source-heading-row" if heading else "sentence-row"
    item = {language: translations[language] for language in ("zh-Hant", "en", "ja", "ko")}
    if THAI_LETTER_RE.search(thai):
        source = [
            "              <div data-thai-unit>",
            f'                <div data-thai lang="th">{escaped(thai)}</div>',
            f'                <div data-romanization lang="th-Latn">{escaped(romanization)}</div>',
            "              </div>",
        ]
    else:
        source = [
            '              <div data-source-text-unit data-source-language="en">',
            f'                <div data-source-text lang="en">{escaped(thai)}</div>',
            "              </div>",
        ]
    return "\n".join([
        f'            <div class="{classes}" data-content-unit>',
        *source,
        f'              {render_translation(item, "zh-Hant")}',
        f'              {render_translation(item, "en", True)}',
        f'              {render_translation(item, "ja", True)}',
        f'              {render_translation(item, "ko", True)}',
        "            </div>",
    ])


def render_main_unit(unit: dict[str, str], lesson: int, sequence: int) -> str:
    page = str(unit["page"])
    if page != main_page(lesson, sequence):
        raise ValueError(f"Unexpected source page {page} for L{lesson} main #{sequence}")
    return "\n".join([
        f'          <article data-content-unit data-source-unit data-source-category="main" data-source-lesson="{lesson}" data-source-sequence="{sequence}" data-source-page="{page}">',
        f"            {page_badge(page)}",
        "            <div data-thai-unit>",
        f'              <div data-thai lang="th">{escaped(unit["thai"])}</div>',
        f'              <div data-romanization lang="th-Latn">{escaped(unit["romanization"])}</div>',
        "            </div>",
        f'            {render_translation(unit, "zh-Hant")}',
        f'            {render_translation(unit, "en", True)}',
        f'            {render_translation(unit, "ja", True)}',
        f'            {render_translation(unit, "ko", True)}',
        "          </article>",
    ])


def render_supporting_unit(
    item: dict[str, str], lesson: int, category: str, sequence: int, line_translations: dict
) -> str:
    page = str(item["page"])
    if item.get("thaiBody"):
        key = f"{category}-{sequence}"
        translations = line_translations.get(key)
        thai_lines = item["thaiBody"].splitlines()
        romanization_lines = item["romanizationBody"].splitlines()
        if translations is None or len(translations) != len(thai_lines):
            raise ValueError(f"L{lesson} {key}: line translations do not match Thai body")
        if len(romanization_lines) != len(thai_lines):
            raise ValueError(f"L{lesson} {key}: romanization lines do not match Thai body")
        rows = [
            render_sentence_row(
                item["thai"],
                item["romanization"],
                heading_translations(item),
                True,
            )
        ]
        rows.extend(
            render_sentence_row(thai, romanization, translated)
            for thai, romanization, translated in zip(
                thai_lines, romanization_lines, translations, strict=True
            )
        )
        return "\n".join([
            f'          <article data-source-unit data-source-category="{category}" data-source-lesson="{lesson}" data-source-sequence="{sequence}" data-source-page="{escaped(page)}">',
            f"            {page_badge(page)}",
            *rows,
            "          </article>",
        ])
    return "\n".join([
        f'          <article data-content-unit data-source-unit data-source-category="{category}" data-source-lesson="{lesson}" data-source-sequence="{sequence}" data-source-page="{escaped(page)}">',
        f"            {page_badge(page)}",
        "            <div data-thai-unit>",
        f'              <div data-thai lang="th">{escaped(item["thai"])}</div>',
        f'              <div data-romanization lang="th-Latn">{escaped(item["romanization"])}</div>',
        "            </div>",
        f'            {render_translation(item, "zh-Hant")}',
        f'            {render_translation(item, "en", True)}',
        f'            {render_translation(item, "ja", True)}',
        f'            {render_translation(item, "ko", True)}',
        "          </article>",
    ])


def render_section(
    lesson: int,
    index: int,
    category: str,
    units: list[dict],
    sequence_start: int,
    kind: str = "",
    line_translations: dict | None = None,
) -> str:
    if category == "main":
        zh_heading = "完整對話" if kind == "dialogue" else "完整閱讀"
        en_heading = "Full dialogue" if kind == "dialogue" else "Full reading"
        rendered = "\n".join(
            render_main_unit(unit, lesson, sequence)
            for sequence, unit in enumerate(units, start=sequence_start)
        )
    else:
        zh_heading, en_heading = SECTION_HEADINGS[category]
        rendered = "\n".join(
            render_supporting_unit(unit, lesson, category, sequence, line_translations or {})
            for sequence, unit in enumerate(units, start=sequence_start)
        )
    return "\n".join([
        f'      <section class="lesson-section" id="lesson-{lesson}-section-{index}" data-source-section data-source-category="{category}">',
        f'        <span class="section-label">Lesson {lesson}</span>',
        f'        <h2 data-ui-copy><span lang="zh-Hant">{zh_heading}</span><span lang="en">{en_heading}</span></h2>',
        '        <div class="content-card">',
        rendered,
        "        </div>",
        "      </section>",
    ])


def render_lesson(main: dict, support: dict, exercise: dict, line_translations: dict) -> str:
    lesson = main["lesson"]
    categories = {
        "main": main["units"],
        "vocabulary": support["vocabulary"],
        "notes": support["notes"],
        "grammar": support["grammar"],
        "exercise": exercise["exercises"],
    }
    seen = {category: [] for category in categories}
    sections = []
    for index, (category, start, end) in enumerate(exercise["layout"], start=1):
        if category not in categories or start < 1 or end < start or end > len(categories[category]):
            raise ValueError(f"Invalid L{lesson} layout block: {category} {start}–{end}")
        seen[category].extend(range(start, end + 1))
        sections.append(
            render_section(
                lesson,
                index,
                category,
                categories[category][start - 1:end],
                start,
                main["kind"],
                line_translations,
            )
        )
    for category, units in categories.items():
        expected = list(range(1, len(units) + 1))
        if seen[category] != expected:
            raise ValueError(f"L{lesson} layout does not cover {category} exactly once: {seen[category]}")
    return "\n".join(sections)


def main() -> None:
    main_data = json.loads(MAIN_CONTENT_PATH.read_text(encoding="utf-8"))
    support_data = json.loads(SUPPORTING_CONTENT_PATH.read_text(encoding="utf-8"))
    exercise_data = json.loads(EXERCISE_CONTENT_PATH.read_text(encoding="utf-8"))
    translations_by_lesson = {
        lesson: json.loads((LINE_TRANSLATIONS_DIR / f"lesson-{lesson}.json").read_text(encoding="utf-8"))
        for lesson in range(1, 9)
    }
    support_by_lesson = {item["lesson"]: item for item in support_data["lessons"]}
    exercise_by_lesson = {item["lesson"]: item for item in exercise_data["lessons"]}
    page_lessons: dict[str, list[dict]] = {}
    for lesson_data in main_data["lessons"]:
        page_lessons.setdefault(PAGE_BY_LESSON[lesson_data["lesson"]], []).append(lesson_data)

    for filename, lessons in page_lessons.items():
        path = ROOT / "level-4" / filename
        page = path.read_text(encoding="utf-8")
        for lesson_data in lessons:
            lesson = lesson_data["lesson"]
            pattern = re.compile(
                rf'      <section class="lesson-section" id="lesson-{lesson}-section-1".*?(?=      <section class="lesson-section" id="lesson-{lesson + 1}"|    </div>\n    <footer class="page-footer")',
                re.DOTALL,
            )
            replacement = render_lesson(
                lesson_data,
                support_by_lesson[lesson],
                exercise_by_lesson[lesson],
                translations_by_lesson[lesson],
            ) + "\n"
            page, replacements = pattern.subn(replacement, page, count=1)
            if replacements != 1:
                raise RuntimeError(f"Expected one generated block for Lesson {lesson}, found {replacements}")
        path.write_text(page, encoding="utf-8")
        print(f"Rendered {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
