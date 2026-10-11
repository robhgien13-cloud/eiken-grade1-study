# CEFR source disagreement audit

## Method
Compare exact case-insensitive `headword + part of speech` keys from CEFR-J v1.5 and Octanove C1/C2 v1.0. Original source files remain unchanged. This is a key-level comparison; different senses may legitimately have different CEFR levels.

## Results
- CEFR-J records: 7799; unique keys: 7798; keys occurring multiple times: 1.
- Octanove records: 2136; unique keys: 2076; keys occurring multiple times: 58.
- Keys shared by both sources: 95.
- Combined unique keys: 9779.

### Level-pair counts
- B2 → C2: 38
- B2 → C1: 21
- B1 → C2: 15
- B1 → C1: 8
- A2 → C1: 6
- A1 → C1: 3
- A2 → C2: 2
- B2 → C1/C2: 1
- A1 → C2: 1

### Sample shared entries (first 25 by Octanove source order)
| Headword | POS | CEFR-J | Octanove |
| --- | --- | --- | --- |
| complexity | noun | B2 | C1 |
| wing | noun | B1 | C1 |
| conceive | verb | B2 | C1 |
| conceivable | adjective | B2 | C1 |
| humble | adjective | B2 | C1 |
| cast | noun | B2 | C1 |
| cast | verb | B2 | C1 |
| tomb | noun | B2 | C1 |
| lap | noun | B2 | C1 |
| exploit | verb | B2 | C1 |
| fit | adjective | A2 | C1 |
| drive | verb | A2 | C1 |
| drive | noun | A1 | C1 |
| pupil | noun | B1 | C1 |
| withdrawal | noun | B2 | C1 |
| talkative | adjective | B1 | C1 |
| recite | verb | B1 | C1 |
| ecstasy | noun | B1 | C1 |
| ecstatic | adjective | B2 | C1 |
| nature | noun | A2 | C1 |
| automatically | adverb | A2 | C1 |
| calf | noun | B1 | C1 |
| dispensable | adjective | B2 | C1 |
| indispensable | adjective | B2 | C1 |
| innovation | noun | B2 | C1 |

## Interpretation and safeguards
- Do not overwrite a source's CEFR level with the other source's label.
- A level difference is not proof of an error: sources may differ in sense, context, pedagogy, or methodology.
- Preserve source attribution, version, headword, POS, and level as separate records.
- EIKEN Grade 1 relevance must be validated against legally usable exam-derived vocabulary/frequency statistics, not inferred from CEFR alone.
- Current audit does **not** establish EIKEN past-paper coverage, frequency, or a learner-specific priority score.
