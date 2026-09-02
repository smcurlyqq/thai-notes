#!/usr/bin/env python3
"""Render the complete Level 4 dialogue/reading sections into the static pages."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "level-4" / "lesson-content.json"
PAGE_BY_LESSON = {
    1: "l1-2.html",
    2: "l1-2.html",
    3: "l3-4.html",
    4: "l3-4.html",
    5: "l5-6.html",
    6: "l5-6.html",
    7: "l7-8.html",
    8: "l7-8.html",
}


def escaped(value: str) -> str:
    return html.escape(value, quote=True)


def render_unit(unit: dict[str, str], lesson: int, sequence: int) -> str:
    return "\n".join(
        [
            f'          <article data-content-unit data-source-unit data-source-lesson="{lesson}" data-source-sequence="{sequence}">',
            "            <div data-thai-unit>",
            f'              <div data-thai lang="th">{escaped(unit["thai"])}</div>',
            f'              <div data-romanization lang="th-Latn">{escaped(unit["romanization"])}</div>',
            "            </div>",
            f'            <div data-translation="zh-Hant" lang="zh-Hant">{escaped(unit["zh-Hant"])}</div>',
            f'            <div data-translation="en" lang="en" data-extra-language>{escaped(unit["en"])}</div>',
            f'            <div data-translation="ja" lang="ja" data-extra-language>{escaped(unit["ja"])}</div>',
            f'            <div data-translation="ko" lang="ko" data-extra-language>{escaped(unit["ko"])}</div>',
            "          </article>",
        ]
    )


def render_section(lesson_data: dict) -> str:
    lesson = lesson_data["lesson"]
    kind = lesson_data["kind"]
    zh_heading = "完整對話" if kind == "dialogue" else "完整閱讀"
    en_heading = "Full dialogue" if kind == "dialogue" else "Full reading"
    units = "\n".join(
        render_unit(unit, lesson, sequence)
        for sequence, unit in enumerate(lesson_data["units"], start=1)
    )
    return "\n".join(
        [
            f'      <section class="lesson-section" id="lesson-{lesson}-section-1" data-source-section>',
            f'        <span class="section-label">Lesson {lesson}</span>',
            f'        <h2 data-ui-copy><span lang="zh-Hant">{zh_heading}</span><span lang="en">{en_heading}</span></h2>',
            '        <div class="content-card">',
            units,
            "        </div>",
            "      </section>",
        ]
    )


def main() -> None:
    data = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    page_lessons: dict[str, list[dict]] = {}
    for lesson_data in data["lessons"]:
        page_lessons.setdefault(PAGE_BY_LESSON[lesson_data["lesson"]], []).append(lesson_data)

    for filename, lessons in page_lessons.items():
        path = ROOT / "level-4" / filename
        page = path.read_text(encoding="utf-8")
        for lesson_data in lessons:
            lesson = lesson_data["lesson"]
            pattern = re.compile(
                rf'      <section class="lesson-section" id="lesson-{lesson}-section-1"[^>]*>.*?      </section>',
                re.DOTALL,
            )
            page, replacements = pattern.subn(render_section(lesson_data), page, count=1)
            if replacements != 1:
                raise RuntimeError(f"Expected one source section for Lesson {lesson}, found {replacements}")
        path.write_text(page, encoding="utf-8")
        print(f"Rendered {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
