#!/usr/bin/env python3
"""Check every Thai row in level-5/source against its declared textbook page.

Usage: verify_level5_against_pdf.py /path/to/textbook.pdf [lesson ...]
Printed page = PDF page - 1. Elevator notices and other image-only pages have no
text layer, so they are listed for visual checking instead of being passed.
The PDF drops the sara am mark, so comparison ignores tone marks and treats it as sara aa.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKS = str.maketrans("ำ่้๊๋์ํ", "า      ")


def norm(text: str) -> str:
    return "".join(re.findall(r"[ก-ฮะ-ฺเ-๎]", text.translate(MARKS)))


def page_text(pdf: str, printed: int) -> str:
    raw = subprocess.run(
        ["pdftotext", "-raw", "-f", str(printed + 1), "-l", str(printed + 1), pdf, "-"],
        capture_output=True, text=True, check=True).stdout
    # Choice labels printed under underlined words interrupt the sentence in the text layer.
    return "".join(n for n in map(norm, raw.splitlines()) if not re.fullmatch(r"[กขคง]+", n))


def source_path(name: str) -> Path:
    prefix = "" if name.startswith("review-") else "lesson-"
    return ROOT / "level-5" / "source" / f"{prefix}{name}.txt"


def main() -> int:
    pdf, lessons = sys.argv[1], sys.argv[2:] or [p.stem.replace("lesson-", "") for p in sorted((ROOT / "level-5/source").glob("*.txt"))]
    failed = 0
    for lesson in lessons:
        page, hay, checked, visual = None, "", 0, set()
        for number, line in enumerate(source_path(lesson).read_text(encoding="utf-8").splitlines(), 1):
            fields = line.split(" | ")
            if line.startswith("@"):
                continue
            if line.startswith("# "):
                page = fields[0].split()[2]
                numbers = [int(x) for x in page.split("–")]
                # A block marked "image" is text inside a picture on a page that also has normal text.
                hay = "" if fields[0].endswith(" image") else "".join(page_text(pdf, n) for n in range(numbers[0], numbers[-1] + 1))
                thai = fields[1]
            else:
                thai = fields[0]
            if len(hay) < 80:
                visual.add(page)
                continue
            # An underlined-choice row lists words from the sentence above; checked by eye.
            if thai.startswith("[ก."):
                visual.add(f"{page} underlined")
                continue
            pieces = [p for p in re.split(r":", thai)]
            checked += 1
            for piece in pieces:
                wanted = norm(piece)
                if wanted and wanted not in hay:
                    failed += 1
                    print(f"lesson-{lesson}:{number} p.{page} NOT FOUND: {piece[:70]}")
        # Reverse direction: every text line on a declared page must be in this lesson's data.
        lines = source_path(lesson).read_text(encoding="utf-8").splitlines()
        everything = norm(" ".join(l.split(" | ")[1] if l.startswith(("@", "# ")) else l.split(" | ")[0] for l in lines))
        pages = set()
        for l in lines:
            if l.startswith("# "):
                numbers = [int(x) for x in l.split(" | ")[0].split()[2].split("–")]
                pages.update(range(numbers[0], numbers[-1] + 1))
        total = 0
        for printed in sorted(pages):
            raw = subprocess.run(["pdftotext", "-raw", "-f", str(printed + 1), "-l", str(printed + 1), pdf, "-"],
                                 capture_output=True, text=True, check=True).stdout
            for text in raw.splitlines():
                wanted = norm(text)
                if len(wanted) < 2 or re.fullmatch(r"[กขคง]+", wanted):  # choice labels under underlines
                    continue
                total += 1
                if wanted not in everything:
                    failed += 1
                    print(f"lesson-{lesson} p.{printed} MISSING FROM DATA: {text[:70]}")
        print(f"lesson {lesson}: {checked} rows checked; {total} page lines checked; image-only pages to check by eye: {sorted(visual)}")
    print("FAILED" if failed else "OK", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
