# thai-notes

Static multilingual Thai study notes published with GitHub Pages.

## Level 4 complete-source workflow

Lessons 1–8 contain 443 ordered, page-labelled units: 100 dialogue/reading units in `level-4/lesson-content.json`; 221 vocabulary, 26 note, and 60 grammar units in `level-4/supporting-content.json`; and 36 complete in-lesson exercise blocks in `level-4/exercise-content.json`. Every unit has Thai, tone-marked romanization, and `zh-Hant` / `en` / `ja` / `ko` translations. The explicit lesson layout preserves textbook interleaving such as grammar → exercise → the next grammar subsection.

Install the authoring and verification dependencies in an isolated environment with `pip install -r scripts/requirements-level4.txt`.

After editing the structured data, rebuild and run both repository audits:

```bash
python3 scripts/build_level4_source_sections.py
python3 scripts/audit_level4_source.py
python3 /path/to/agent-core/skills/thai-notes/scripts/audit_thai_notes.py .
```

When the local source PDF is available, independently verify declared pages and source examples:

```bash
python3 scripts/verify_level4_against_pdf.py /path/to/source.pdf
```

`level-4/source-manifest.json` is deliberately frozen. Do not update it during a normal build. Only after rechecking every changed Thai source unit against the original source may you run:

```bash
python3 scripts/freeze_level4_source_manifest.py
```

The audit has hard-coded per-lesson and per-category inventory counts, so deleting an item and regenerating the manifest cannot make an incomplete set pass. It also fails when an item is changed, duplicated, reordered, assigned the wrong page, rendered with a missing language, or loses line-aligned romanization.
