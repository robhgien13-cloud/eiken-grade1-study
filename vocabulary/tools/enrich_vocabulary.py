#!/usr/bin/env python3
"""Enrich CEFR source records on demand without republishing third-party datasets.

Install: pip install -r requirements.txt
Usage: python vocabulary/tools/enrich_vocabulary.py --limit 100 --output vocabulary/analysis/sample-enriched.csv
Omit --limit to process all rows. Output contains third-party-derived metadata;
review licenses before committing generated outputs to a public repository.
"""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ("CEFR-J", ROOT / "vocabulary/raw/cefrj-vocabulary-profile-1.5.csv"),
    ("Octanove", ROOT / "vocabulary/raw/octanove-vocabulary-profile-c1c2-1.0.csv"),
]

def source_rows():
    for name, path in SOURCES:
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                yield name, row

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=0, help="0 = all records")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    from wordfreq import zipf_frequency
    import cmudict
    pronunciations = cmudict.dict()
    try:
        import wn
        lexicon = wn.Wordnet("oewn:2024")
    except Exception:
        lexicon = None  # WordNet corpus is an optional separate download.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["source", "headword", "pos", "cefr", "zipf_en", "cmu_pronunciation", "wordnet_synsets"]
    with args.output.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        for i, (name, row) in enumerate(source_rows()):
            if args.limit and i >= args.limit:
                break
            word = row["headword"]
            prons = pronunciations.get(word.lower(), [])
            synsets = ""
            if lexicon is not None:
                try:
                    synsets = ";".join(s.id for s in lexicon.synsets(word)[:5])
                except Exception:
                    pass
            writer.writerow({
                "source": name, "headword": word, "pos": row["pos"],
                "cefr": row["CEFR"], "zipf_en": zipf_frequency(word, "en"),
                "cmu_pronunciation": " / ".join(" ".join(p) for p in prons[:2]),
                "wordnet_synsets": synsets,
            })
    print("Wrote", args.output)

if __name__ == "__main__":
    main()
