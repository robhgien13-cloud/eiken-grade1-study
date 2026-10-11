# Official EIKEN Grade 1 exam PDF: first-pass audit (2026-10-11)

GitHub Actions run: https://github.com/robhgien13-cloud/eiken-grade1-study/actions/runs/38120230259

Successfully fetched and extracted official question-booklet and listening-script PDFs for 2026-1, 2025-3 and 2026-2. The last session is reserved as holdout for subsequent vocabulary coverage evaluation. No exam text is republished.

## Provisional figures (2026-1)
- Reading proxy: 10 pages, 3,954 tokens / 1,570 distinct word forms; CEFR headword-unmatched 746 distinct forms.
- Listening script: 9 pages, 3,995 tokens / 1,404 distinct word forms; CEFR headword-unmatched 542 distinct forms.
- Reading proxy Zipf >=5: 2,393/3,954 tokens (60.5%); Listening Zipf >=5: 2,789/3,995 tokens (69.8%).
- Reading proxy Zipf <3: 235/3,954 tokens (5.9%); Listening Zipf <3: 73/3,995 tokens (1.8%).

## Important limitations
- Question-booklet pages 3–12 are a rough proxy, NOT isolated reading passages; vocabulary choices and instructions are mixed.
- Listening scripts include directions, question prompts and other non-conversation text.
- Word forms are not lemmatized; unmatched CEFR forms are NOT synonymous with advanced vocabulary.
- CEFR label is chosen as highest level when a headword appears at several levels. Sense/POS is not disambiguated.
- Zipf score is a frequency metric, not a ranked vocabulary size.
- Official PDFs may have extracted layout noise. Review PDF structure before deriving cutoffs.
- The 2026-2 holdout has been descriptively audited but should not be used to select thresholds; reserve it for independent evaluation.

## Next analysis
1. Separate actual Reading passage sections from vocabulary questions and directions, and Listening dialogue/monologue from directions.
2. Lemmatize and normalize, audit proper nouns/OCR/text-extraction artifacts.
3. Compute coverage curves by Zipf thresholds and by EIKEN-source-list membership on development sessions only.
4. Select thresholds and validate on held-out 2026-2.
