# Level 4 source audit

Audit date: 2026-09-02

This report covers the complete Thai `บทสนทนา` / `บทอ่าน` for Lessons 1–8. The local source document itself is not stored in this public repository.

## Inventory

| Lesson | Type | Source units | Source section coverage |
| --- | --- | ---: | --- |
| 1 | Dialogue | 13 | Exact |
| 2 | Reading | 20 | Exact |
| 3 | Dialogue | 16 | Exact |
| 4 | Reading | 8 | Exact |
| 5 | Dialogue | 15 | Exact |
| 6 | Reading | 12 | Exact |
| 7 | Dialogue | 11 | Exact |
| 8 | Reading | 5 | Exact |
| **Total** |  | **100** | **Exact** |

Dialogue units use one speaker turn per unit. Reading units use one source paragraph per unit. The Lesson 1 time transition and Lesson 3 location line are preserved as their own units.

## Verification performed

1. Extracted the complete source section from `บทสนทนา` / `บทอ่าน` through the start of `คำศัพท์` for every lesson.
2. Removed extraction-only page headers, footnote numbers, whitespace, and the source font's alternate encoding of `ำ` for comparison only.
3. Compared the entire remaining Thai character stream with all inventory units joined in order. All eight lessons matched exactly, including total character counts.
4. Frozen each lesson's unit count and order-sensitive Thai SHA-256 in `level-4/source-manifest.json`.
5. Compared `lesson-content.json`, the frozen manifest, and rendered HTML. Missing, extra, modified, duplicated, or reordered source units cause the audit to fail.

The human-readable translations and romanization remain separate review dimensions; structural or source-fidelity success does not by itself certify translation quality.
