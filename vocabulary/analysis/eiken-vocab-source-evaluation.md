# eiken-vocab source evaluation (2026-10-11)

## Decision
**Candidate for an EIKEN-specific calibration signal, NOT yet approved for bulk ingestion.** No other-exam data is needed. Preserve the independent CEFR-J / Octanove source labels.

## Verified from upstream
- Repository: https://github.com/pnsk-lab/eiken-vocab
- README: PDF preprocessing -> LLM extraction -> AST -> unigram/phrase counting -> per-grade scores -> AI-generated translations/examples.
- Input notebook: `nakasyou/eiken-pdf` dataset; filters `year >= 2020`. This is a **filter in code**, not evidence that every year/session was actually processed.
- Output asset exists: `viewer/src/assets/metadata.jsonl` (~18.2 MB). Contents/row count/coverage **not verified**: connected file reader returned no text for line-limited fetch.
- Schema includes `word`, `isPhrase`, `meanings`, `score`, `count`, `rank`, `isTypo` for grades 1, pre1, 2, pre2, 3, 4, 5.
- Grade score in `steps/5-build-vocablist/main.ipynb` is a smoothed log probability contrast between the target grade and pooled lower grades; it is **not** an official EIKEN difficulty rating. The code additionally merges unigram/phrase ranks.
- Repository LICENSE is MIT (2025 Shotaro Nakamura), but that does not independently license source exam PDFs or any derived copyrighted passages, nor automatically settle rights to AI-generated examples.

## Proposed data strategy
1. **EIKEN calibration**: official past papers + independently verified eiken-vocab metadata, segregating vocabulary question correct answers, distractors, reading text, listening transcript where source allows. Do not equate all occurrences.
2. **Candidate universe**: license-cleared CEFR-J, Octanove and other high-level vocabulary lists; keep source, POS, sense, and level as separate observations.
3. **Auxiliary features**: wordfreq usage frequency; WordNet senses; CMUdict pronunciation. No other exams.
4. **Ranking**: keep separate fields for EIKEN evidence, CEFR, general frequency, topical coverage, and uncertainty. No EIKEN occurrence must mean 'unobserved', not 'unimportant'.
5. **Validation**: hold out whole EIKEN exam sessions/years; evaluate recall of difficult unseen words, not just matching already-seen tokens. Avoid leakage between training and evaluation.

## Before ingesting eiken-vocab metadata
- Obtain full metadata.jsonl and verify JSONL parse rate, row count, duplicate keys, score/count/rank distribution and grade coverage.
- Establish actual source years, administrations, grades and reading/listening coverage from artifacts or provenance; code alone is insufficient.
- Review source PDF terms and redistribution rights. Do not copy source exam passages, question text, or LLM examples into the public repository without permission.
- Spot-check extraction/lemmatization, sense ambiguity, distractors, hallucinated definitions, and spurious grade scores.

## Status
Research and design documented. **No third-party vocabulary entries ingested, no score empirically validated, no copyright clearance asserted.**
