# Level 4 complete source audit

Audit date: 2026-09-03

Source: `TH4_Textbook_On-site_Sep-Oct_2026.pdf` (local only; the PDF is not stored in this public repository).

Scope: Lessons 1–8, every in-lesson item in textbook order. This includes the complete dialogue/reading, complete vocabulary list, every numbered textbook note, every grammar explanation/example, and every comprehension, grammar, speaking, and sentence-writing exercise. Pair-review and final-exam sections have their own separate site scope. Each included item carries the printed textbook page number.

## Frozen inventory

| Lesson | Dialogue / reading | Vocabulary | Notes | Grammar | Exercise blocks | Total | Lesson pages |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 13 | 19 | 6 | 7 | 6 | 51 | 7–19 |
| 2 | 20 | 37 | 0 | 9 | 4 | 70 | 20–30 |
| 3 | 16 | 17 | 5 | 15 | 4 | 57 | 37–47 |
| 4 | 8 | 27 | 0 | 7 | 4 | 46 | 48–56 |
| 5 | 15 | 12 | 9 | 6 | 4 | 46 | 63–73 |
| 6 | 12 | 48 | 0 | 6 | 3 | 69 | 74–83 |
| 7 | 11 | 25 | 6 | 5 | 3 | 50 | 89–98 |
| 8 | 5 | 36 | 0 | 5 | 8 | 54 | 99–110 |
| **Total** | **100** | **221** | **26** | **60** | **36** | **443** |  |

## Textbook order

Each lesson has an explicit layout inventory made of category slices. The renderer follows that inventory verbatim, including repeated category blocks. When an exercise interrupts a grammar chapter, the exercise remains at that point and the next grammar subsection follows it, exactly as in the textbook.

## Verification contract

- The auditor has hard-coded per-lesson counts for all five categories; re-freezing a reduced file cannot make the audit pass.
- Every unit must have a valid page or page range inside its lesson's source bounds.
- The frozen manifest hashes page + Thai heading + Thai source body in order for every category.
- The rendered HTML must match the source data by lesson, category, sequence, page, Thai text, romanization, and all four translations.
- Section order must match each lesson's frozen page-layout inventory, including grammar/exercise interleaving.
- Every Thai source body must have a non-empty romanization body.
- Chinese fields fail if they contain Japanese kana or Hangul; Korean fields fail if they lack Hangul or contain Japanese kana; English fields fail if they contain CJK/Hangul text.
- Included data and rendered pages fail if PDF extraction artifacts appear.
- The independent PDF verifier checks every exercise source line plus every main, vocabulary, note, and grammar source anchor/example on the declared page.

Passing this audit proves structural coverage, order, pages, and field wiring. Translation and pronunciation still require human/visual review in the actual site path before publication.
