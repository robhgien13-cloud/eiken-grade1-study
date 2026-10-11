# eiken-vocab metadata: full-file audit (2026-10-11)

## Source and method
- Upstream: https://github.com/pnsk-lab/eiken-vocab/blob/main/viewer/src/assets/metadata.jsonl
- Retrieved via GitHub contents connector; parsed each JSONL record and inspected per-grade score/count/rank. This is a **source-data audit**, not a copyright clearance or empirical score validation.
- Raw upstream vocabulary and AI-generated examples were **not** copied into this repository.

## Verified counts
| Metric | Count |
|---|---:|
| Total JSONL records | 21,997 |
| Successfully parsed | 21,997 |
| Invalid JSON | 0 |
| Distinct `word` strings (exact case-sensitive) | 21,985 |
| Repeated `word` strings | 12 |
| `isPhrase=false` records | 8,545 |
| `isPhrase=true` records | 13,452 |
| `isTypo=true` records | 1,253 |
| Empty `meanings` arrays | 5 |
| Records with positive grade-1 `count` | 9,223 |
| Records with numeric grade-1 `score` | 21,983 |

Per-grade records with positive count (overlap across grades): grade 1 9,223; pre1 6,249; 2 5,011; pre2 3,915; 3 2,379; 4 1,687; 5 639.

## Critical interpretation
- A record is a unigram or phrase; 21,997 records **does not mean 21,997 distinct single words**.
- Grade `count` is a transformed/aggregated pipeline metric, **not verified as the number of distinct exam appearances**. The notebook uses sublinear `log1p` counts and later casts values to integers.
- Grade `score` is relative to lower grades, not CEFR or an official EIKEN score. `rank` is normalized, not a literal ordinal position.
- Examples of high grade-1-ranked unigrams with grade-1 positive count include `impoverished`, `subsidy`, `exploit`, `treaty`, `extinction`, `usury`. Presence does not certify accurate translation or sense.
- Source-year coverage is still unverified: code filters upstream input to year >= 2020, but published metadata does not retain year/session provenance.
- The MIT license on upstream code does not independently clear redistribution of EIKEN source material or LLM-generated example text.

## Decision and next checks
1. Treat as a **candidate independent EIKEN-grade calibration signal**; exclude typo-flagged entries and inspect duplicates and empty meanings.
2. Cross-match normalized unigrams with CEFR-J and Octanove. Preserve grade-1 evidence and source CEFR as independent features.
3. Validate sample high-rank and low-rank words against actual EIKEN source sessions, distinguishing reading/listening/vocabulary options where possible.
4. Never infer `count=0` means irrelevant; hold out full sessions for validation and do not use other exams.
5. Before publishing a derived dataset, verify rights and limit public output to independently licensed data, source metadata, and original aggregate statistics.

Status: **full JSONL parsed and aggregate audit completed; CEFR cross-match and year/session provenance pending.**
