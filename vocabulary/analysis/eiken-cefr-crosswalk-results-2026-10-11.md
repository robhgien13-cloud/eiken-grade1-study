# EIKEN × CEFR crosswalk — 2026-10-11

GitHub Actions: https://github.com/robhgien13-cloud/eiken-grade1-study/actions/runs/38119674402

## Results
- Input JSONL lines: 21,997; missing word: 6.
- Excluded isTypo: 1,248; excluded phrase entries: 12,924.
- Eligible unigram entries: **7,819**.
- Exact casefolded headword matches to CEFR-J / Octanove: **4,923**; among them **4,858** have at least one POS match; **65** match headword only.
- No exact headword match: **2,896** (not necessarily advanced).
- Grade 1 occurrence count >0 among eligible unigrams: **4,778**.
- Grade 1 occurrence and CEFR headword match: **3,390**.
- C1/C2 matched entries: **478**; of these Grade 1 occurrence count >0: **285**.
- Counts of matched levels (can overlap): A1 920, A2 1,080, B1 1,615, B2 1,308, C1 303, C2 179.

## Limits
The crosswalk matches surface headwords; it does not establish same sense or EIKEN-specific difficulty. The 2,896 unmatched entries may include morphology, misspellings, or source coverage gaps. 12,924 phrase records remain for a separate matching pass. Year/session and reading/listening coverage cannot be inferred from this dataset. No raw upstream vocabulary entries were committed.

## Next steps
1. Review unmatched words via morphology and POS, quarantine noise.
2. Keep Grade 1 observed and relative score separate; rank candidates with independent CEFR and frequency features.
3. Verify source-year/session coverage and set aside unseen EIKEN exams for evaluation.
4. Audit licensing before publishing any row-level derived list.
