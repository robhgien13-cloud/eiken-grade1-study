# eiken-vocab metadata audit — 2026-10-11

Run: https://github.com/robhgien13-cloud/eiken-grade1-study/actions/runs/38119580554
Status: SUCCESS. Audited upstream `viewer/src/assets/metadata.jsonl` by streaming, without copying vocabulary entries.

## Measured counts

| Metric | Count |
|---|---:|
| JSONL nonempty lines | 21,997 |
| Valid records with word | 21,991 |
| Unigram records | 8,539 |
| Phrase records | 13,452 |
| Distinct casefolded word + isPhrase keys | 21,984 |
| Duplicate word/type keys | 7 |
| Missing word | 6 |
| isTypo true | 1,248 |
| Positive grade 1 occurrence count | 9,223 |
| Grade 1 score field numeric | 21,983 |
| Grade 1 score > 0 | 15,921 |
| Grade 1 rank field numeric | 21,991 |
| Malformed meanings (limited schema check) | 0 |

## Interpretation and caveats

- `count['1'] > 0` is evidence of an upstream computed occurrence, **not** proof of distinct exam vocabulary, verified year coverage, or necessity for learners.
- `score['1'] > 0` (15,921) is a relative grade comparison and does not mean that every record occurred in Grade 1. Do not use as an inclusion gate by itself.
- No row-level verification of AI translations, examples, corpus accuracy or copyright clearance was performed.
- Exact year/session coverage and split of reading vs listening are still unknown from metadata.
- The audit checked duplicates by casefolded word and phrase flag, not by meaning or lemma.

## Next validation

1. Build a non-redistributive crosswalk with CEFR-J/Octanove keyed by normalized lemma and POS when available.
2. Keep separate `observed_grade1`, `relative_grade1_score`, `cefr`, `general_frequency`, `source` and `uncertainty`.
3. Exclude or quarantine `isTypo` entries and audit missing grade-1 scores before any study-list import.
4. Verify exam year/session coverage and whether source questions, choices, reading and listening are separable; hold out sessions for validation.
5. Confirm upstream rights before importing any row-level content into this public repository.

No external vocabulary rows imported in this audit.
