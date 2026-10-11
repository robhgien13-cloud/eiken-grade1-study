#!/usr/bin/env python3
"""Audit upstream eiken-vocab metadata without republishing its content."""
import collections
import json
import sys
import urllib.request

URL = "https://raw.githubusercontent.com/pnsk-lab/eiken-vocab/main/viewer/src/assets/metadata.jsonl"
GRADES = ("1", "pre1", "2", "pre2", "3", "4", "5")

def main():
    counts = collections.Counter()
    seen = set()
    positive = collections.Counter()
    nonzero = collections.Counter()
    grade_score_present = collections.Counter()
    rank_present = collections.Counter()
    invalid_examples = 0
    with urllib.request.urlopen(URL, timeout=120) as response:
        for line in response:
            if not line.strip():
                continue
            counts["lines"] += 1
            try:
                row = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                counts["invalid_json"] += 1
                continue
            if not isinstance(row, dict):
                counts["invalid_record"] += 1
                continue
            word = row.get("word")
            if not isinstance(word, str) or not word.strip():
                counts["missing_word"] += 1
                continue
            key = (word.casefold().strip(), bool(row.get("isPhrase")))
            if key in seen:
                counts["duplicate_word_type"] += 1
            seen.add(key)
            counts["valid_records"] += 1
            counts["phrases" if row.get("isPhrase") else "unigrams"] += 1
            if row.get("isTypo"):
                counts["marked_typo"] += 1
            if not isinstance(row.get("meanings"), list):
                counts["missing_meanings"] += 1
            else:
                if any(not isinstance(m, dict) or not isinstance(m.get("translation"), str) for m in row["meanings"]):
                    invalid_examples += 1
            scores = row.get("score") or {}
            occur = row.get("count") or {}
            ranks = row.get("rank") or {}
            for grade in GRADES:
                if isinstance(scores.get(grade), (int, float)):
                    grade_score_present[grade] += 1
                    if scores[grade] > 0:
                        positive[grade] += 1
                if isinstance(occur.get(grade), (int, float)) and occur[grade] > 0:
                    nonzero[grade] += 1
                if isinstance(ranks.get(grade), (int, float)):
                    rank_present[grade] += 1
    result = {
        "source": URL, "note": "Metadata only; years/sessions and copyright clearance cannot be inferred from this file",
        "counts": dict(counts), "unique_word_type": len(seen),
        "positive_grade_score_records": dict(positive),
        "nonzero_grade_count_records": dict(nonzero),
        "grade_score_present": dict(grade_score_present),
        "grade_rank_present": dict(rank_present),
        "malformed_meanings_records": invalid_examples,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if counts["invalid_json"] or counts["valid_records"] == 0 else 0

if __name__ == "__main__":
    sys.exit(main())
