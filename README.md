# thai-notes

Static multilingual Thai study notes published with GitHub Pages.

## Level 4 source workflow

The complete Lesson 1–8 dialogue/reading content lives in `level-4/lesson-content.json`. Each source unit contains exact Thai text, tone-marked romanization, and `zh-Hant` / `en` / `ja` / `ko` translations.

Normal edits use this order:

```bash
python3 scripts/build_level4_source_sections.py
python3 scripts/audit_level4_source.py
```

`level-4/source-manifest.json` is deliberately frozen. Do not update it during a normal build. Only after rechecking every changed Thai source unit against the original source may you run:

```bash
python3 scripts/freeze_level4_source_manifest.py
```

The audit fails when a source unit is missing, added, changed, duplicated, or reordered between the structured content, frozen manifest, and rendered HTML.
