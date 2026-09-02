#!/usr/bin/env python3
"""Deliberately freeze Level 4 source counts and order-sensitive hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "level-4" / "lesson-content.json"
MANIFEST_PATH = ROOT / "level-4" / "source-manifest.json"


def digest(units: list[dict[str, str]]) -> str:
    payload = "\n".join(unit["thai"] for unit in units).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    data = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    lessons = []
    for lesson in data["lessons"]:
        lessons.append(
            {
                "lesson": lesson["lesson"],
                "kind": lesson["kind"],
                "unitCount": len(lesson["units"]),
                "orderedThaiSha256": digest(lesson["units"]),
            }
        )
    manifest = {
        "schemaVersion": 1,
        "scope": data["scope"],
        "totalUnitCount": sum(item["unitCount"] for item in lessons),
        "lessons": lessons,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Frozen {MANIFEST_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
