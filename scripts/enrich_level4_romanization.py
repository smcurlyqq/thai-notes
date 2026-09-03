#!/usr/bin/env python3
"""Fill Level 4 supporting-content romanization without changing source order.

Run with a Python environment containing ``thaiphon`` and
``thaiphon-data-volubilis``. Existing hand-reviewed spellings in the rendered
Level 4 pages take precedence over generated Paiboon+ output.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

os.environ.setdefault("PYTHAINLP_DATA_DIR", str(Path(tempfile.gettempdir()) / "pythainlp-data"))

from pythainlp.tokenize import word_tokenize
from thaiphon import transcribe


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "level-4" / "supporting-content.json"
EXERCISE_PATH = ROOT / "level-4" / "exercise-content.json"
MAIN_CONTENT_PATH = ROOT / "level-4" / "lesson-content.json"

# Dictionary/compound readings that the phonology engine cannot segment
# reliably. Keep this list small, explicit, and source-reviewable.
OVERRIDES = {
    "เมื่อก่อน": "mʉ̂a-gɔ̀ɔn",
    "กรดไหลย้อน": "gròt-lǎi-yɔ́ɔn",
    "ขี้ผึ้ง": "kîi-pʉ̂ng",
    "น้ำลาย": "náam-laai",
    "พิษสุนัขบ้า": "phít-sù-nák-bâa",
    "วัดความดันเลือด": "wát-kwaam-dan-lʉ̂at",
    "เพลงสรรเสริญพระบารมี": "phleeng-sǎn-sə̌ən-phrá-baa-rá-mii",
    "พระมหากษัตริย์": "phrá-má-hǎa-gà-sàt",
    "เข้าเมืองตาหลิ่ว ต้องหลิ่วตาตาม": "kâo-mʉang-dtaa-lìw dtɔ̂ng-lìw-dtaa-dtaam",
    "โหราศาสตร์": "hǒo-raa-sàat",
    "ดาราศาสตร์": "daa-raa-sàat",
    "ทะเยอทะยาน": "thá-yəə-thá-yaan",
    "เอื้อเฟื้อเผื่อแผ่": "ʉ̂a-fʉ́a-phʉ̀a-phɛ̀ɛ",
    "เจ้ากี้เจ้าการ": "jâo-gîi-jâo-gaan",
    "อัธยาศัยดี": "àt-thá-yaa-sǎi-dii",
    "งานแต่งงาน": "ngaan-dtɛ̀ng-ngaan",
    "บ้านพักคนชรา": "bâan-phák-khon-chá-raa",
    "ความรับผิดชอบ": "kwaam-ráp-phìt-chɔ̂ɔp",
    "บุคลิกภาพ": "bùk-khá-lík-gà-phâap",
    "ใคร ๆ": "krai-krai",
    "ต่าง ๆ": "dtàang-dtàang",
    "(ช่าง)เห็นอกเห็นใจ": "(châang) hěn-òk-hěn-jai",
    "ช่วงวัย": "chûang-wai",
    "เธอควรเอาร่มไปเผื่อฝนตก": "thəə-khuan-ao-rôm-bpai-phʉ̂a-fǒn-dtòk",
    "ผู้หญิงคนนั้นผิวค๊าว ขาว": "pûu-yǐng-khon-nán-phǐw-káao-kǎao",
    "ผิว": "phǐw",
    "ค๊าว": "káao",
}


def existing_readings() -> dict[str, str]:
    data = json.loads(MAIN_CONTENT_PATH.read_text(encoding="utf-8"))
    return {
        unit["thai"].strip(): unit["romanization"].strip()
        for lesson in data["lessons"]
        for unit in lesson["units"]
    }


def romanize(text: str, existing: dict[str, str]) -> str:
    clean = text.strip()
    if not clean:
        return ""
    if clean in OVERRIDES:
        return OVERRIDES[clean]
    if clean in existing:
        return existing[clean]
    # Segment long Thai explanations into words before phonological
    # transcription. Passing a whole unsegmented paragraph to the engine can
    # create bogus readings or silently drop a phrase.
    rendered: list[str] = []
    previous_was_thai = False
    previous_reading = ""
    for token in word_tokenize(clean, keep_whitespace=True):
        is_thai = bool(re.search(r"[\u0E00-\u0E7F]", token))
        if not is_thai:
            rendered.append(token)
            previous_was_thai = False
            continue
        duplicated = re.fullmatch(r"(.+?)\s*ๆ", token)
        if duplicated:
            base = duplicated.group(1)
            base_reading = OVERRIDES.get(base, transcribe(base, scheme="paiboon_plus"))
            reading = f"{base_reading}-{base_reading}"
        elif token == "ๆ":
            reading = previous_reading or "mai-ya-mók"
        elif token == "ฯ":
            reading = "lá"
        else:
            reading = OVERRIDES.get(token, transcribe(token, scheme="paiboon_plus"))
        if not reading:
            raise ValueError(f"No romanization generated for Thai token: {token!r}")
        if previous_was_thai:
            rendered.append(" ")
        rendered.append(reading)
        previous_was_thai = True
        previous_reading = reading
    return re.sub(r"[ \t]+", " ", "".join(rendered)).strip()


def replace_thai_in_translation(text: str, existing: dict[str, str]) -> str:
    """Use Latin readings when an explanation needs to name a Thai form."""
    def replace(match: re.Match[str]) -> str:
        value = match.group(0)
        if value == "ๆ":
            return "mai-ya-mók"
        return romanize(value, existing)

    return re.sub(r"[\u0E00-\u0E7F]+", replace, text)


def main() -> None:
    data = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    exercise_data = json.loads(EXERCISE_PATH.read_text(encoding="utf-8"))
    existing = existing_readings()
    for lesson in data["lessons"]:
        vocab_objects = []
        for item in lesson["vocabulary"]:
            if isinstance(item, dict):
                page = item["page"]
                thai = item["thai"]
                en = item["en"]
                zh = item["zh-Hant"]
                ja = item["ja"]
                ko = item["ko"]
            else:
                page, thai, en, zh, ja, ko = item
            vocab_objects.append(
                {
                    "page": str(page),
                    "thai": thai,
                    "romanization": romanize(thai, existing),
                    "zh-Hant": zh,
                    "en": en,
                    "ja": ja,
                    "ko": ko,
                }
            )
        lesson["vocabulary"] = vocab_objects
        for section in ("notes", "grammar"):
            for item in lesson[section]:
                item["romanization"] = romanize(item["thai"], existing)
                item["romanizationBody"] = "\n".join(
                    romanize(line, existing) for line in item["thaiBody"].splitlines()
                )
        for section in ("vocabulary", "notes", "grammar"):
            for item in lesson[section]:
                for language in ("zh-Hant", "en", "ja", "ko"):
                    item[language] = replace_thai_in_translation(item[language], existing)
    CONTENT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for lesson in exercise_data["lessons"]:
        for item in lesson["exercises"]:
            item["romanization"] = romanize(item["thai"], existing)
            item["romanizationBody"] = "\n".join(
                romanize(line, existing) for line in item["thaiBody"].splitlines()
            )
            for language in ("zh-Hant", "en", "ja", "ko"):
                item[language] = replace_thai_in_translation(item[language], existing)
    EXERCISE_PATH.write_text(
        json.dumps(exercise_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Enriched {CONTENT_PATH.relative_to(ROOT)} and {EXERCISE_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
