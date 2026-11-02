#!/usr/bin/env python3
"""Freeze Level 5 counts and ordered page + Thai hashes.

A normal build never runs this. Run it only after rechecking changed text against
the textbook; audit_level5_source.py fails on any drift until then.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_level5_source import MANIFEST_PATH, source_inventory


def main() -> None:
    inventory = source_inventory()
    manifest = {
        "schemaVersion": 1,
        "scope": "level-5-lessons-1-8-review-1-4-final-exam-sample-complete-textbook-order",
        "totalUnitCount": sum(c["unitCount"] for s in inventory.values() for c in s.values()),
        "sections": inventory,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"froze {manifest['totalUnitCount']} units in {MANIFEST_PATH.name}")


if __name__ == "__main__":
    main()
