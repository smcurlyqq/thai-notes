#!/usr/bin/env python3
"""Render Level 5 lesson pages from level-5/source/lesson-N.txt in textbook order."""
from __future__ import annotations

import html
import re
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "level-5" / "source"
PAGES = {"l1-2.html": (1, 2), "l3-4.html": (3, 4), "l5-6.html": (5, 6), "l7-8.html": (7, 8)}
LANGS = ("zh-Hant", "en", "ja", "ko")
LABELS = {
    "main": ("完整課文", "Full reading"),
    "vocabulary": ("完整單字", "Complete vocabulary"),
    "grammar": ("語言運用", "Language use"),
    "exercise": ("課本練習", "Textbook exercises"),
    "listening": ("聽力原文", "Listening script"),
}
e = lambda s: html.escape(s, quote=True)


def parse(path: Path) -> dict:
    lesson, blocks = None, []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        fields = line.split(" | ")
        if line.startswith("@"):
            kind, number = fields[0][1:].split()
            lesson = {"kind": kind, "number": int(number), "row": fields[1:]}
        elif line.startswith("# "):
            category, page = fields[0][2:].split()[:2]
            blocks.append({"category": category, "page": page, "heading": fields[1:], "rows": []})
        else:
            blocks[-1]["rows"].append(fields)
        expected = 7 if line.startswith(("@", "# ")) else 6
        if len(fields) != expected:
            raise ValueError(f"{path.name}:{number}: expected {expected} fields, got {len(fields)}")
    return {**lesson, "blocks": blocks}


def row(fields: list[str], heading: bool = False) -> str:
    th, rom, *tr = fields
    cls = "sentence-row source-heading-row" if heading else "sentence-row"
    if re.search(r"[\u0E01-\u0E2E\u0E30-\u0E3A\u0E40-\u0E4E]", th):
        source = [
            "              <div data-thai-unit>",
            f'                <div data-thai lang="th">{e(th)}</div>',
            f'                <div data-romanization lang="th-Latn">{e(rom)}</div>',
            "              </div>",
        ]
    else:
        # A row printed in English has nothing to romanize.
        source = [
            '              <div data-source-text-unit data-source-language="en">',
            f'                <div data-source-text lang="en">{e(th)}</div>',
            "              </div>",
        ]
    parts = [f'            <div class="{cls}" data-content-unit>', *source]
    for lang, text in zip(LANGS, tr, strict=True):
        extra = "" if lang == "zh-Hant" else " data-extra-language"
        parts.append(f'              <div class="translation-body" data-translation="{lang}" lang="{lang}"{extra}>{e(text)}</div>')
    parts.append("            </div>")
    return "\n".join(parts)


def vocabulary_row(fields: list[str]) -> list[str]:
    """The textbook prints an English gloss beside each word; it belongs in the EN row, not the Thai line."""
    return [re.sub(r"\s*\(?[A-Za-z].*$", "", fields[0]), *fields[1:]]


def article(block: dict, lesson, sequence: int) -> str:
    page = block["page"]
    prefix = "pp." if "–" in page else "p."
    return "\n".join([
        f'          <article data-source-unit data-source-category="{block["category"]}" data-source-lesson="{lesson}" '
        f'data-source-sequence="{sequence}" data-source-page="{page}">',
        f'            <span class="source-page" data-source-page-label>{prefix} {page}</span>',
        row(block["heading"], True),
        *[row(vocabulary_row(r) if block["category"] == "vocabulary" else r) for r in block["rows"]],
        "          </article>",
    ])


def lesson_html(data: dict) -> str:
    n = data["number"]
    review = data["kind"] == "review"
    key = f"review-{n}" if review else f"lesson-{n}"
    label = ("Final Exam Sample" if n == 5 else f"Review {n}") if review else f"Lesson {n}"
    out = [
        f'      <section class="lesson-section" id="{key}">',
        f'        <span class="section-label">{label}</span>',
        f'        <h2 data-ui-copy><span lang="zh-Hant">{e(data["row"][2])}</span><span lang="en">{e(data["row"][3])}</span></h2>',
        '        <div class="content-card">',
        row(data["row"]).replace("sentence-row", "lesson-title-row"),
        "        </div>",
        "      </section>",
    ]
    counts: dict[str, int] = {}
    runs = groupby(data["blocks"], key=lambda b: b["category"])
    for index, (category, blocks) in enumerate(runs, 1):
        zh, en = LABELS[category]
        out += [
            f'      <section class="lesson-section" id="{key}-section-{index}" data-source-section data-source-category="{category}">',
            f'        <span class="section-label">{label}</span>',
            f'        <h2 data-ui-copy><span lang="zh-Hant">{zh}</span><span lang="en">{en}</span></h2>',
            '        <div class="content-card">',
        ]
        for block in blocks:
            counts[category] = counts.get(category, 0) + 1
            out.append(article(block, key if review else n, counts[category]))
        out += ["        </div>", "      </section>"]
    return "\n".join(out)


def page(name: str, lessons: list[dict]) -> str:
    a, b = name[1:-5].split("-")
    toc = "\n".join(
        f'        <a href="#lesson-{d["number"]}" data-ui-copy><span lang="zh-Hant">第 {d["number"]} 課</span><span lang="en">Lesson {d["number"]}</span></a>'
        for d in lessons
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lessons {a}–{b} · Thai Notes Level 5</title>
  <link rel="stylesheet" href="../assets/site.css">
  <script src="../assets/language-toggle.js" defer></script>
</head>
<body data-page-type="lesson" data-level="5" data-lessons="{a}-{b}" class="level-5">
  <main class="site-shell">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="../index.html" data-ui-copy><span lang="zh-Hant">所有 Level</span><span lang="en">All Levels</span></a>
      <span aria-hidden="true">›</span>
      <a href="index.html" data-ui-copy><span lang="zh-Hant">Level 5 首頁</span><span lang="en">Level 5 Home</span></a>
    </nav>
    <header class="site-header level-5">
      <p class="eyebrow">Intensive Thai · Level 5</p>
      <h1>Lessons {a}–{b}</h1>
      <p class="lede" data-ui-copy><span lang="zh-Hant">第 {a}–{b} 課完整講義</span><span lang="en">Lessons {a}–{b} complete notes</span></p>
      <nav class="lesson-toc" aria-label="Page sections">
{toc}
      </nav>
    </header>
    <div class="language-toolbar">
      <button type="button" data-language-toggle aria-expanded="false">顯示 EN · JP · KR / Show EN · JP · KR</button>
    </div>
    <div class="lesson-layout">
{chr(10).join(lesson_html(d) for d in lessons)}
    </div>
    <footer class="page-footer" data-ui-copy><span lang="zh-Hant">Thai Notes · 羅馬讀音永遠顯示</span><span lang="en">Romanization is always visible</span></footer>
  </main>
</body>
</html>
"""


def exam_page(reviews: list[dict]) -> str:
    toc = "\n".join(
        f'        <a href="#review-{d["number"]}" data-ui-copy><span lang="zh-Hant">{e(d["row"][2])}</span><span lang="en">{e(d["row"][3])}</span></a>'
        for d in reviews
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Exam Review · Thai Notes Level 5</title>
  <link rel="stylesheet" href="../assets/site.css">
  <script src="../assets/language-toggle.js" defer></script>
</head>
<body data-page-type="exam-review" data-level="5" class="level-5">
  <main class="site-shell">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="../index.html" data-ui-copy><span lang="zh-Hant">所有 Level</span><span lang="en">All Levels</span></a>
      <span aria-hidden="true">›</span>
      <a href="index.html" data-ui-copy><span lang="zh-Hant">Level 5 首頁</span><span lang="en">Level 5 Home</span></a>
    </nav>
    <header class="site-header level-5">
      <p class="eyebrow">Intensive Thai · Level 5</p>
      <h1>Exam Review</h1>
      <p class="lede" data-ui-copy><span lang="zh-Hant">複習題與期末模擬考</span><span lang="en">Review exercises and final exam sample</span></p>
      <nav class="lesson-toc" aria-label="Page sections">
{toc}
      </nav>
    </header>
    <div class="language-toolbar">
      <button type="button" data-language-toggle aria-expanded="false">顯示 EN · JP · KR / Show EN · JP · KR</button>
    </div>
    <div class="lesson-layout">
{chr(10).join(lesson_html(d) for d in reviews)}
    </div>
    <footer class="page-footer" data-ui-copy><span lang="zh-Hant">Thai Notes · 羅馬讀音永遠顯示</span><span lang="en">Romanization is always visible</span></footer>
  </main>
</body>
</html>
"""


def main() -> None:
    for name, numbers in PAGES.items():
        lessons = [parse(SOURCE / f"lesson-{n}.txt") for n in numbers if (SOURCE / f"lesson-{n}.txt").exists()]
        if lessons:
            (ROOT / "level-5" / name).write_text(page(name, lessons), encoding="utf-8")
            rows = sum(len(b["rows"]) + 1 for d in lessons for b in d["blocks"])
            print(f"level-5/{name}: lessons {[d['number'] for d in lessons]}, {rows} rows")
    reviews = [parse(path) for path in sorted(SOURCE.glob("review-*.txt"))]
    if reviews:
        (ROOT / "level-5" / "exam-review.html").write_text(exam_page(reviews), encoding="utf-8")
        rows = sum(len(b["rows"]) + 1 for d in reviews for b in d["blocks"])
        print(f"level-5/exam-review.html: reviews {[d['number'] for d in reviews]}, {rows} rows")


if __name__ == "__main__":
    main()
