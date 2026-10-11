# Official EIKEN Grade 1 extraction and normalization status — 2026-10-11

Successful workflow: https://github.com/robhgien13-cloud/eiken-grade1-study/actions/runs/38120409797

| Session | Reading pages 6-11: tokens | Reading lemma types | Listening tokens | Listening lemma types |
|---|---:|---:|---:|---:|
| 2026-1 | 2,875 | 999 | 3,715 | 1,205 |
| 2025-3 | 2,881 | 998 | unavailable (source PDF HTTP 404) | unavailable |
| 2026-2 (holdout) | 2,971 | 1,092 | 3,670 | 1,206 |

Reading pages 3-5 (vocabulary multiple-choice), 12-14 (Writing), 16-22 (listening answer choices) are excluded from the reading sample. Reading pages 6-11 still include comprehension questions and answer choices, so this is not yet a clean reading-passage-only corpus. Listening scripts have headers and some instructions removed heuristically, but further segmentation QA is required. Words are tokenized and lemmatized with simplemma (context-free), with original word-form and lemma counts reported. No source text is republished.

Status: STEP 1 PARTIAL, STEP 2 PARTIAL. Remaining: remove all reading question/choice text, review listening prompts, proper nouns and lemmatization errors, and recover 2025-3 listening PDF. Do not use these metrics as final vocabulary cutoff evidence.
