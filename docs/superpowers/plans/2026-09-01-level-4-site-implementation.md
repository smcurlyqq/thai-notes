# Thai Notes Level 4 implementation plan

Date: 2026-09-01 (Asia/Taipei)

## Scope

Implement the approved Level 3–9 navigation design, migrate every existing Level 3 page without breaking its public URL, and add complete Level 4 notes for Lessons 1–8 plus Exam Review. The site remains plain static HTML, CSS, and JavaScript.

## Source map

Use the local Level 4 source only during authoring. Do not add the source file, its filename, local path, watermark, or publisher material to the repository.

| Output | Relevant source pages | Note sections |
| --- | --- | --- |
| `level-4/l1-2.html` | 7–31 | L1 dialogue, vocabulary, language use, grammar; L2 reading, vocabulary, grammar |
| `level-4/l3-4.html` | 37–57 | L3 dialogue, vocabulary, language use, grammar; L4 reading, vocabulary, grammar |
| `level-4/l5-6.html` | 63–84 | L5 dialogue, vocabulary, language use, grammar; L6 reading, vocabulary, grammar |
| `level-4/l7-8.html` | 89–110 | L7 dialogue, vocabulary, language use, grammar; L8 reading, vocabulary, grammar |
| `level-4/exam-review.html` | 117–132 plus lesson notes | Consolidated vocabulary, grammar, examples, and exam reminders; do not reproduce answer sheets |

Review exercises on pages 32–36, 58–62, 85–89, and 112–117 are used to confirm emphasis and common confusions, not copied wholesale.

## Implementation sequence

1. Add `assets/site.css` and `assets/language-toggle.js` using the approved no-JavaScript-safe language behavior.
2. Replace the root homepage with all-Level navigation for Level 3–9.
3. Move existing Level 3 content to `level-3/`, add a Level homepage, and replace every former root content URL with a query/hash-preserving redirect.
4. Convert Level 3 learning units to the shared content contract. Preserve Thai, Traditional Chinese, English, Japanese, page titles, and URLs; add Korean and always-visible tone-marked romanization.
5. Add the Level 4 homepage and four combined lesson pages. Use concise study notes containing each lesson's core passage/dialogue, tested vocabulary, grammar, examples, and key points.
6. Add Level 4 Exam Review as a study guide rather than a copy of the source exam.
7. Run the `thai-notes` auditor with site scope, then manually verify translation and romanization alignment.
8. Preview desktop and mobile layouts in the mbqq browser. Test the language toggle, keyboard focus, navigation, and legacy redirects.
9. Summarize the final diff. Commit and push only after Amber explicitly approves and the shared sync gate is clear.
10. After GitHub is verified, create and re-fetch the `thai-notes` skill record in Notion `AI 資產總覽 → assets`.

## Content contract

- Interface text always displays Traditional Chinese and English.
- Learning content defaults to Thai, tone-marked romanization, and Traditional Chinese.
- One button controls English, Japanese, and Korean translations together.
- Raw HTML keeps all translations visible; JavaScript activates the default hidden state.
- Every independent learning unit contains one `zh-Hant`, `en`, `ja`, and `ko` translation.
- Every Thai learning string has one adjacent `th-Latn` romanization.
- No language preference persists across pages.

## Verification

- All required Level 3 and Level 4 files exist.
- Every internal link and fragment resolves.
- All eight former Level 3 root URLs redirect correctly with query and hash preserved.
- The structural auditor passes with zero issues.
- `git diff --check` passes.
- No local path, source filename, source asset, watermark text, or unfinished marker appears in public files.
- Browser checks cover all-Level navigation, both Level homepages, all four Level 4 lesson pages, Exam Review, one converted Level 3 lesson page, and every redirect type at desktop and mobile widths.
