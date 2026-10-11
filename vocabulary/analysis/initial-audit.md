# Initial vocabulary audit

| Source | CSV data rows | CEFR distribution |
| --- | ---: | --- |
| CEFR-J v1.5 | 7799 | {"A1":1164,"A2":1411,"B1":2446,"B2":2778} |
| Octanove C1/C2 v1.0 | 2136 | {"C1":1111,"C2":1025} |

- Exact matching headword + POS keys between sources: **95**.
- Unique keys in CEFR-J: **7798**.
- Unique keys in Octanove: **2076**.
- Combined unique headword + POS keys: **9779**.

Comparison is case-insensitive and trims headword and POS. This is a preliminary key-level audit, not a semantic overlap, EIKEN coverage or corpus-frequency analysis. Counts are based on CSV data lines, not independent dictionary senses.
